import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from langchain_community.document_loaders import TextLoader
from app.core.config import settings
from app.services.rag.vs_instance import vs
from app.services.rag.vector_service import VectorService
from pathlib import Path

logger = logging.getLogger(__name__)

class ProjectWatcherHandler(FileSystemEventHandler):
    def __init__(self, vector_service: VectorService):
        self.vs = vector_service
        # Extensions à surveiller (Code + Admin)
        self.valid_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.css', '.html', 
            '.md', '.json', '.yaml', '.yml', '.env', 
            '.pdf', '.xlsx', '.xls', '.csv'
        }
        self.ignore_dirs = {'node_modules', '.git', '__pycache__', 'dist', 'build', '.next', 'data', '.venv', 'venv'}

    def on_modified(self, event):
        if self._should_handle(event):
            logger.info(f"🔄 Fichier modifié : {event.src_path}")
            self._ingest_file(event.src_path)

    def on_created(self, event):
        if self._should_handle(event):
            logger.info(f"🆕 Nouveau fichier : {event.src_path}")
            self._ingest_file(event.src_path)

    def _should_handle(self, event):
        if event.is_directory:
            return False
        
        path = Path(event.src_path)
        # Vérifier l'extension
        if path.suffix not in self.valid_extensions and path.name != '.env':
            return False
            
        # Vérifier si c'est dans un dossier à ignorer
        for part in path.parts:
            if part in self.ignore_dirs:
                return False
        
        return True

    def _ingest_file(self, file_path):
        try:
            # On laisse un petit délai pour que l'écriture du fichier soit terminée
            import time
            time.sleep(1.0)
            
            if not Path(file_path).exists():
                return

            loader = TextLoader(file_path, encoding='utf-8')
            docs = loader.load()
            
            if docs:
                self.vs.add_documents(docs)
                print(f"--- 🚀 WATCHDOG SUCCESS : {file_path} ingéré ---", flush=True)
            else:
                print(f"--- ⚠️ WATCHDOG SKIP : {file_path} est vide ---", flush=True)
        except Exception as e:
            print(f"--- ❌ WATCHDOG ERROR ({file_path}): {e} ---", flush=True)
            logger.error(f"❌ Erreur ingestion {file_path}: {e}")

def start_watcher():
    """Démarre le thread de surveillance des fichiers en utilisant l'instance globale vs."""
    path = settings.TARGET_PROJECT_PATH
    
    event_handler = ProjectWatcherHandler(vs)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    print(f"--- 👀 WATCHDOG DÉMARRÉ SUR: {path} ---", flush=True)
    return observer
