import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.agents.graph import workflow, get_checkpointer
from app.api.endpoints import chat, threads, system
import os
from pathlib import Path

# Logging configuration
class SensitiveFilter(logging.Filter):
    def filter(self, record):
        msg = str(record.msg)
        sensitive_keys = ["api_key", "X-Vibrisse-Api-Key", "llm_api_key"]
        for key in sensitive_keys:
            if key in msg:
                import re
                record.msg = re.sub(fr"{key}['\"]?\s*[:=]\s*['\"]?([^'\"\s]+)", fr"{key}: [REDACTED]", msg)
        return True

# Silencer les bibliothèques trop verbeuses
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Filtrer les logs d'accès uvicorn pour les routes techniques (health, etc.)
class NoNoiseFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        # On cache les pollings incessants
        noise_paths = ["/api/system/health", "/api/system/config", "/api/threads/"]
        return not any(path in msg for path in noise_paths)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addFilter(SensitiveFilter())
logging.getLogger("uvicorn.access").addFilter(NoNoiseFilter())

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application (Démarrage/Arrêt)."""
    
    async def background_onboarding():
        try:
            await asyncio.sleep(1)
            await settings.load_manifest()
            print("--- 🧠 ONBOARDING COMPLETED IN BACKGROUND ---", flush=True)
        except Exception as e:
            logger.error(f"Background onboarding failed: {e}")

    async with get_checkpointer() as saver:
        app.state.agent = workflow.compile(checkpointer=saver, interrupt_before=["sensitive_tools"])
        app.state.saver = saver
        from app.services.rag.vs_instance import vs
        app.state.vs = vs
        asyncio.create_task(background_onboarding())
        from app.services.core.watcher_service import start_watcher
        watcher = start_watcher()
        print("--- ✅ BACKEND READY ---", flush=True)
        yield
        watcher.stop()
        watcher.join()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. ROUTES API (AVEC PRÉFIXES COHÉRENTS) ---
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(threads.router, prefix="/api/threads", tags=["threads"])
app.include_router(system.router, prefix="/api/system", tags=["system"])

# --- 2. SERVEUR FRONTEND ---
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"

if frontend_path.exists():
    # Montage du dossier assets pour la performance
    app.mount("/assets", StaticFiles(directory=frontend_path / "assets"), name="static_assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        # On laisse passer les routes API
        if full_path.startswith("api") or full_path.startswith("/api"):
            return None
        
        # On vérifie si le fichier existe physiquement dans dist (ex: vite.svg, robots.txt, fonts/...)
        file_path = frontend_path / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
            
        # Par défaut, on renvoie l'index.html pour le routing SPA
        return FileResponse(frontend_path / "index.html")
else:
    logger.warning(f"Frontend dist folder not found at {frontend_path}")
