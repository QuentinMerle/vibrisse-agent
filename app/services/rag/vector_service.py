import asyncio
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_classic.retrievers import ParentDocumentRetriever, EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_classic.storage import LocalFileStore, create_kv_docstore
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
            # Dossier data relatif au projet Vibrisse
            base_dir = Path(__file__).parent.parent.parent / "data"
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
            base_dir = Path(__file__).parent.parent.parent / "data"
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
        
        try:
            # On groupe les documents par splitter pour optimiser l'indexation
            docs_by_splitter = {}
            for doc in documents:
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
        retriever = self.get_hybrid_retriever()
        return await retriever.ainvoke(query)

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
        """Scan intelligent : ignore les dossiers inutiles (node_modules, .git, etc.)"""
        from langchain_community.document_loaders import TextLoader
        print(f"--- 📂 RE-INDEXATION INTELLIGENTE : {target_path} ---", flush=True)
        
        valid_extensions = {".py", ".js", ".jsx", ".ts", ".tsx", ".css", ".html", ".md", ".json", ".yaml", ".yml"}
        ignore_dirs = {"node_modules", ".git", ".gemini", "__pycache__", "dist", "build", "venv", ".venv", "data"}
        
        all_docs = []
        for root, dirs, files in os.walk(target_path):
            # Filtrage des dossiers
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in valid_extensions:
                    file_path = os.path.join(root, file)
                    try:
                        loader = TextLoader(file_path, encoding='utf-8')
                        all_docs.extend(loader.load())
                    except: pass
        
        if all_docs:
            self.add_documents(all_docs)
            print(f"✅ RE-INDEXATION RÉUSSIE : {len(all_docs)} fichiers sources indexés.", flush=True)
        else:
            print("⚠️ Aucun fichier source trouvé.", flush=True)

    async def list_indexed_files(self):
        def _scan():
            try:
                keys = list(self.store.yield_keys())
                if not keys: return []
                all_documents = [doc for doc in self.store.mget(keys) if doc]
                from app.core.config import settings
                files = {os.path.relpath(doc.metadata.get("source", ""), settings.TARGET_PROJECT_PATH) for doc in all_documents if doc.metadata.get("source")}
                return sorted(list(files))
            except Exception as e: 
                print(f"Error listing files: {e}")
                return []
        return await asyncio.to_thread(_scan)