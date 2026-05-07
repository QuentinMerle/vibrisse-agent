import os
import subprocess
import psutil
import httpx
import logging
from typing import Optional
from fastapi import APIRouter, Request, BackgroundTasks
from app.core.config import settings
from app.services.llm.model_service import fetch_model_context_limit, get_available_models
from app.services.core.watcher_service import watcher_service

from app.services.core.system_discovery import system_discovery

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/discovery")
async def get_system_discovery():
    """Découvre les ressources système (RAM, VRAM, GPU)."""
    return system_discovery.get_system_info()

@router.get("/config-check")
async def config_check():
    """Vérifie les variables de configuration actives."""
    return {
        "ragas_model": settings.RAGAS_MODEL,
        "ragas_embedding_model": settings.RAGAS_EMBEDDING_MODEL,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "target_path": settings.TARGET_PROJECT_PATH
    }

@router.get("/health")
async def health_check():
    """Vérifie la santé globale du backend et la connexion à Ollama."""
    health = {
        "status": "ok",
        "ollama": "disconnected",
        "vectorstore": "ok"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.LLM_BASE_URL}/api/tags", timeout=2.0)
            if response.status_code == 200:
                health["ollama"] = "connected"
    except Exception:
        health["status"] = "error"
        health["ollama"] = "disconnected"

    if not os.path.exists("./data/chroma_db"):
        health["vectorstore"] = "initializing"

    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    # Sur macOS, pour coller au Moniteur d'Activité : 
    # Used = Total - Available (où Available = Free + Inactive)
    real_used_gb = (mem.total - mem.available) / (1024**3)
    
    health["ram"] = {
        "used": round(real_used_gb, 1),
        "total": round(mem.total / (1024**3), 1),
        "percent": round((real_used_gb / (mem.total / (1024**3))) * 100, 1),
        "swap_used": round(swap.used / (1024**3), 1),
        "swap_total": round(swap.total / (1024**3), 1),
        "swap_percent": swap.percent
    }

    return health

@router.get("/models")
async def list_models(provider: str = "ollama", api_key: Optional[str] = None):
    """Liste les modèles disponibles pour un provider spécifique."""
    models = await get_available_models(provider, api_key)
    return {"models": models}

@router.get("/models/limit/{model_name}")
async def get_model_limit(model_name: str):
    limit = await fetch_model_context_limit(model_name)
    return {"model": model_name, "limit": limit}

@router.get("/capabilities")
async def get_capabilities(provider: str, model: Optional[str] = None):
    """Retourne les capacités techniques d'un modèle spécifié (Vision, Search, etc.)."""
    from app.services.llm.model_service import fetch_model_capabilities
    model_name = model or settings.clean_orchestrator_model
    caps = await fetch_model_capabilities(provider, model_name)
    return caps

@router.get("/config")
async def get_config():
    from app.services.core.session_service import session_service
    limit = await fetch_model_context_limit(settings.clean_orchestrator_model)
    session = session_service.load_session()
    return {
        "model": settings.clean_orchestrator_model,
        "target_path": settings.TARGET_PROJECT_PATH,
        "onboarded": session.get("onboarded", False),
        "context_limit": limit,
        "features": {
            "search": settings.ENABLE_WEB_SEARCH,
            "vision": settings.ENABLE_VISION,
            "expert_review": settings.ENABLE_EXPERT_REVIEW,
            "github": settings.ENABLE_GITHUB
        }
    }

from pydantic import BaseModel
from pathlib import Path

class TargetPathRequest(BaseModel):
    path: str

@router.post("/config/target")
async def update_target_path(request: Request, req: TargetPathRequest, background_tasks: BackgroundTasks):
    """Change le dossier de travail de l'agent et relance l'onboarding."""
    new_path = req.path
    if not os.path.exists(new_path):
        return {"status": "error", "message": f"Le chemin {new_path} n'existe pas."}
    
    # 1. Arrêter la surveillance actuelle
    watcher_service.stop()

    # 2. Mise à jour des settings en mémoire
    settings.TARGET_PROJECT_PATH = new_path
    
    # 3. Vider l'index vectoriel
    try:
        request.app.state.vs.clear_cache()
    except Exception as e:
        logger.warning(f"Could not clear cache during project switch: {e}")

    # 4. Relancer l'onboarding (Manifeste)
    try:
        await settings.load_manifest()
        
        # 5. Lancer la ré-indexation complète en arrière-plan
        background_tasks.add_task(request.app.state.vs.reindex_project, new_path)
        
        # 6. Relancer la surveillance sur le nouveau dossier
        watcher_service.start(new_path)

        return {
            "status": "success", 
            "new_path": new_path,
            "manifest": settings.PROJECT_MANIFEST
        }
    except Exception as e:
        logger.error(f"Failed to re-onboard project at {new_path}: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/cache/clear")
async def clear_cache(request: Request):
    request.app.state.vs.clear_cache()
    return {"status": "cleared"}

@router.get("/files")
async def list_files(request: Request):
    files = await request.app.state.vs.list_indexed_files()
    return {"files": files}

class LLMValidationRequest(BaseModel):
    provider: str
    model: Optional[str] = None
    apiKey: Optional[str] = None

@router.post("/models/pull")
async def pull_model(req: dict, background_tasks: BackgroundTasks):
    """Lance le téléchargement d'un modèle Ollama en arrière-plan de manière asynchrone."""
    model_name = req.get("model")
    if not model_name:
        return {"status": "error", "message": "Modèle requis"}
    
    async def do_pull_async():
        try:
            process = await asyncio.create_subprocess_exec(
                "ollama", "pull", model_name,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await process.wait()
            logger.info(f"Modèle {model_name} téléchargé avec succès (async).")
        except Exception as e:
            logger.error(f"Échec pull async {model_name}: {e}")

    background_tasks.add_task(do_pull_async)
    return {"status": "success", "message": f"Téléchargement de {model_name} lancé."}

@router.post("/validate-llm")
async def validate_llm(req: LLMValidationRequest):
    """Tente une micro-inférence pour valider les paramètres LLM."""
    from app.services.llm.llm_factory import get_llm
    try:
        llm = get_llm(
            provider=req.provider,
            model=req.model,
            api_key=req.apiKey,
            temperature=0,
            streaming=False
        )
        # Timeout court pour ne pas bloquer l'UI
        response = await llm.ainvoke("Réponds uniquement par 'OK'.", config={"timeout": 5000})
        return {"status": "success", "message": "Connexion établie avec succès."}
    except Exception as e:
        logger.error(f"LLM Validation failed for {req.provider}: {e}")
        return {"status": "error", "message": str(e)}

# --- MCP (Model Context Protocol) ROUTES ---

from typing import List, Dict

class MCPConnectRequest(BaseModel):
    server_id: str
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None

@router.post("/mcp/connect")
async def connect_mcp(req: MCPConnectRequest):
    from app.services.mcp.mcp_client import mcp_manager
    try:
        await mcp_manager.connect_stdio(
            server_id=req.server_id,
            command=req.command,
            args=req.args,
            env=req.env
        )
        return {"status": "success", "message": f"Connecté à {req.server_id}"}
    except Exception as e:
        logger.error(f"MCP Connection failed: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/mcp/disconnect/{server_id}")
async def disconnect_mcp(server_id: str):
    from app.services.mcp.mcp_client import mcp_manager
    await mcp_manager.disconnect(server_id)
    return {"status": "success", "message": f"Déconnecté de {server_id}"}

@router.get("/mcp/status")
async def get_mcp_status():
    from app.services.mcp.mcp_client import mcp_manager
    connected = list(mcp_manager.sessions.keys())
    
    # On va aussi essayer de récupérer les outils pour chaque serveur pour l'affichage
    details = []
    for sid in connected:
        try:
            tools = await mcp_manager.get_langchain_tools(sid)
            details.append({"id": sid, "tools_count": len(tools), "tools": [t.name for t in tools]})
        except:
            details.append({"id": sid, "tools_count": 0, "tools": []})
            
    return {"status": "success", "connected_servers": connected, "details": details}

@router.get("/pick-directory")
async def pick_directory():
    """Ouvre un sélecteur de dossier natif sur macOS."""
    # Note: os.name est 'posix' sur macOS
    import platform
    if platform.system() != 'Darwin':
        return {"status": "error", "message": "Cette fonctionnalité n'est disponible que sur macOS pour le moment."}
    
    script = 'POSIX path of (choose folder with prompt "Sélectionnez le dossier de votre projet")'
    try:
        proc = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if proc.returncode == 0:
            path = proc.stdout.strip()
            return {"status": "success", "path": path}
        else:
            return {"status": "cancelled"}
    except Exception as e:
        logger.error(f"Error picking directory: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/onboarding/reset")
async def reset_onboarding():
    """Réinitialise le statut d'onboarding dans la session."""
    from app.services.core.session_service import session_service
    session = session_service.load_session()
    session_service.save_session(
        project_path=session.get("last_project_path", "."),
        manifest=session.get("last_manifest", ""),
        onboarded=False
    )
    return {"status": "success"}

@router.post("/onboarding/complete")
async def complete_onboarding():
    """Marque l'onboarding comme terminé dans la session."""
    from app.services.core.session_service import session_service
    session = session_service.load_session()
    session_service.save_session(
        project_path=session.get("last_project_path", "."),
        manifest=session.get("last_manifest", ""),
        onboarded=True
    )
    return {"status": "success"}

@router.post("/evaluate")
async def evaluate_rag(data: dict):
    """Évalue la qualité d'une réponse RAG via Ragas."""
    from app.services.core.evaluation_service import evaluation_service
    
    question = data.get("question")
    contexts = data.get("contexts", [])
    generation = data.get("generation")
    
    if not all([question, generation]):
        return {"status": "error", "message": "Missing required fields (question, generation)"}
        
    scores = await evaluation_service.evaluate_interaction(
        question=question,
        contexts=contexts,
        generation=generation
    )
    return scores
