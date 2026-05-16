import asyncio
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain.retrievers import ParentDocumentRetriever, EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain.storage import LocalFileStore, create_kv_docstore
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from pathlib import Path
import os

class VectorService:
    def __init__(self):
        self._embeddings = None
        self._vectorstore = None
        self._store = None
        self._cached_hybrid_retriever = None
        
        # Splitter par défaut (utilisé comme fallback)
        self.default_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50
        )
        
        # Cache pour les splitters par langage
        self._splitters = {}

    @property
    def embeddings(self):
        if self._embeddings is None:
            from app.core.config import settings
            self._embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=settings.LLM_BASE_URL)
        return self._embeddings

    @property
    def project_id(self):
        """Génère un ID unique court pour le projet actuel basé sur son chemin."""
        from app.core.config import settings
        import hashlib
        path_hash = hashlib.md5(str(Path(settings.TARGET_PROJECT_PATH).absolute()).encode()).hexdigest()[:8]
        return f"proj_{path_hash}"

    @property
    def vectorstore(self):
        if self._vectorstore is None:
            from app.core.config import settings
            # Dossier data à la racine
            base_dir = Path(__file__).parent.parent.parent.parent / "data"
            persist_dir = str(base_dir / "chroma_db")
            
            # Nom de collection dynamique pour isoler les projets
            col_name = f"code_{self.project_id}"
            print(f"--- 🗄️ COLLECTION VECTORIELLE : {col_name} ---", flush=True)
            
            self._vectorstore = Chroma(
                collection_name=col_name, 
                embedding_function=self.embeddings, 
                persist_directory=persist_dir
            )
        return self._vectorstore

    @property
    def store(self):
        if self._store is None:
            base_dir = Path(__file__).parent.parent.parent.parent / "data"
            store_dir = str(base_dir / "parent_documents" / self.project_id)
            os.makedirs(store_dir, exist_ok=True)
            fs = LocalFileStore(store_dir)
            self._store = create_kv_docstore(fs)
        return self._store

    def get_splitter_for_ext(self, file_path: str):
        """Retourne le splitter adapté au langage du fichier."""
        ext = os.path.splitext(file_path)[1].lower()
        lang_map = {
            ".py": Language.PYTHON,
            ".js": Language.JS,
            ".jsx": Language.JS,
            ".ts": Language.TS,
            ".tsx": Language.TS,
            ".html": Language.HTML,
            ".md": Language.MARKDOWN,
            ".cpp": Language.CPP,
            ".go": Language.GO,
            ".java": Language.JAVA,
            ".php": Language.PHP,
            ".sol": Language.SOL,
            ".rst": Language.RST,
        }
        
        lang = lang_map.get(ext)
        if not lang:
            return self.default_splitter
            
        if lang not in self._splitters:
            self._splitters[lang] = RecursiveCharacterTextSplitter.from_language(
                language=lang,
                chunk_size=400,
                chunk_overlap=50
            )
        return self._splitters[lang]

    def get_retriever(self, splitter=None):
        return ParentDocumentRetriever(
            vectorstore=self.vectorstore, 
            docstore=self.store, 
            child_splitter=splitter or self.default_splitter
        )

    def add_documents(self, documents):
        if not documents: return
        
        # Filtre de sécurité global pour éviter d'indexer du bruit par erreur
        ignore_patterns = {".next/", "node_modules/", "dist/", "build/", ".venv/", "venv/", ".git/", "__pycache__/"}
        
        filtered_docs = []
        for doc in documents:
            source = doc.metadata.get("source", "")
            if any(p in source for p in ignore_patterns):
                continue
            filtered_docs.append(doc)
            
        if not filtered_docs: return
        
        try:
            # On groupe les documents par splitter pour optimiser l'indexation
            docs_by_splitter = {}
            for doc in filtered_docs:
                source = doc.metadata.get("source", "")
                splitter = self.get_splitter_for_ext(source)
                if splitter not in docs_by_splitter:
                    docs_by_splitter[splitter] = []
                docs_by_splitter[splitter].append(doc)

            print(f"--- 📥 INDEXATION HYBRIDE : {len(documents)} documents ---", flush=True)
            
            for splitter, docs in docs_by_splitter.items():
                retriever = self.get_retriever(splitter=splitter)
                retriever.add_documents(docs)
                
            self._cached_hybrid_retriever = None
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ CRITICAL INDEX ERROR: {e}\n{error_details}", flush=True)
            raise e

    async def search(self, query: str):
        from app.services.rag.grep_service import GrepService
        from app.core.config import settings
        
        # 1. Surgical Grep (Fast-Track)
        print(f"--- 🔍 SURGICAL GREP : Scannage rapide du projet... ---", flush=True)
        grep_svc = GrepService(settings.TARGET_PROJECT_PATH)
        grep_results = await asyncio.to_thread(grep_svc.fast_search, query)
        
        # 2. Hybrid Retriever (Semantic + BM25)
        retriever = self.get_hybrid_retriever()
        hybrid_results = await retriever.ainvoke(query)
        
        # 3. Fusion & Dé-doublonnage
        # On met les résultats du Grep en premier car ils sont plus "exacts"
        all_results = grep_results + hybrid_results
        
        seen_sources = set()
        final_results = []
        for doc in all_results:
            source = doc.metadata.get("source")
            if source not in seen_sources:
                final_results.append(doc)
                seen_sources.add(source)
                
        return final_results[:10] # On limite aux 10 meilleurs

    def get_hybrid_retriever(self):
        if self._cached_hybrid_retriever: return self._cached_hybrid_retriever
        
        # Augmentation de k pour la recherche vectorielle initiale (plus de bruit, mais moins d'oublis)
        vector_retriever = self.get_retriever().vectorstore.as_retriever(search_kwargs={"k": 15})
        
        try:
            keys = list(self.store.yield_keys())
            if not keys: return vector_retriever
            
            # TODO: Persister l'index BM25 pour éviter de tout recharger en RAM au boot
            all_documents = [doc for doc in self.store.mget(keys) if doc]
            if not all_documents: return vector_retriever
            
            bm25_retriever = BM25Retriever.from_documents(all_documents)
            bm25_retriever.k = 10 # On prend les 10 meilleurs matches textuels
            
            # Pondération : on donne un peu plus de poids au BM25 pour le code (noms de fonctions)
            self._cached_hybrid_retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, vector_retriever], 
                weights=[0.4, 0.6] 
            )
            return self._cached_hybrid_retriever
        except Exception as e:
            print(f"⚠️ Hybrid Fallback: {e}")
            return vector_retriever

    def clear_cache(self):
        import shutil
        try:
            if self._vectorstore: self._vectorstore.delete_collection()
        except: pass
        for path in [Path("./data/parent_documents"), Path("./data/chroma_db")]:
            if path.exists():
                shutil.rmtree(path)
                path.mkdir(parents=True, exist_ok=True)
        self._vectorstore = None
        self._store = None
        self._cached_hybrid_retriever = None

    def reindex_project(self, target_path: str):
        """Scan intelligent : traite les fichiers par batchs pour éviter l'explosion de RAM."""
        from langchain_community.document_loaders import TextLoader
        print(f"--- 📂 RE-INDEXATION SÉCURISÉE : {target_path} ---", flush=True)
        
        valid_extensions = {".py", ".js", ".jsx", ".ts", ".tsx", ".css", ".html", ".md", ".json", ".yaml", ".yml"}
        ignore_dirs = {
            "node_modules", ".git", ".gemini", "__pycache__", "dist", "build", 
            "venv", ".venv", "data", "out", ".next", ".cache", "logs", "temp", "tmp",
            "coverage", ".pytest_cache", ".idea", ".vscode", ".next"
        }
        
        BATCH_SIZE = 50 # On indexe par paquets de 50 fichiers pour préserver la RAM
        MAX_FILE_SIZE = 1 * 1024 * 1024 # 1 Mo max par fichier
        
        current_batch = []
        total_indexed = 0
        
        for root, dirs, files in os.walk(target_path):
            # Filtrage préventif des dossiers lourds
            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in valid_extensions:
                    file_path = os.path.join(root, file)
                    
                    # Sécurité : Limite de taille individuelle
                    try:
                        if os.path.getsize(file_path) > MAX_FILE_SIZE:
                            continue
                        
                        loader = TextLoader(file_path, encoding='utf-8')
                        current_batch.extend(loader.load())
                        
                        # Si le batch est plein, on indexe et on vide la RAM
                        if len(current_batch) >= BATCH_SIZE:
                            self.add_documents(current_batch)
                            total_indexed += len(current_batch)
                            current_batch = [] # Libération immédiate
                    except Exception as e:
                        print(f"⚠️ Erreur sur {file}: {e}")
                        continue
        
        # On indexe le dernier batch restant
        if current_batch:
            self.add_documents(current_batch)
            total_indexed += len(current_batch)
        
        if total_indexed > 0:
            print(f"✅ RE-INDEXATION RÉUSSIE : {total_indexed} fichiers sources indexés.", flush=True)
        else:
            print("⚠️ Aucun fichier source trouvé ou trop gros.", flush=True)

    async def list_indexed_files(self):
        def _scan():
            try:
                keys = list(self.store.yield_keys())
                if not keys: return {"files": [], "dirs": []}
                all_documents = [doc for doc in self.store.mget(keys) if doc]
                from app.core.config import settings
                
                ignore_patterns = {".next/", "node_modules/", "dist/", "build/", ".venv/", "venv/", ".git/", "__pycache__/"}
                
                files = set()
                dirs = set()
                for doc in all_documents:
                    source = doc.metadata.get("source")
                    if not source: continue
                    
                    if any(p in source for p in ignore_patterns):
                        continue
                        
                    rel_path = os.path.relpath(source, settings.TARGET_PROJECT_PATH)
                    files.add(rel_path)
                    
                    # Extraction des dossiers parents
                    parts = rel_path.split(os.sep)
                    for i in range(1, len(parts)):
                        dirs.add(os.sep.join(parts[:i]))
                
                return {
                    "files": sorted(list(files)),
                    "dirs": sorted(list(dirs))
                }
            except Exception as e: 
                print(f"Error listing files: {e}")
                return {"files": [], "dirs": []}
        return await asyncio.to_thread(_scan)