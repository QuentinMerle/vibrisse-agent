import httpx
import logging
import re
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# Cache pour éviter les appels répétitifs à Ollama
MODEL_LIMITS_CACHE = {}
MODEL_CAPS_CACHE = {}

async def fetch_model_capabilities(provider: str, model_name: str) -> Dict[str, bool]:
    """Détecte dynamiquement les capacités d'un modèle via les APIs des providers."""
    cache_key = f"{provider}:{model_name}"
    if cache_key in MODEL_CAPS_CACHE:
        return MODEL_CAPS_CACHE[cache_key]
    
    caps = {
        "vision": False,
        "search": False,
        "expert_review": True,
        "terminal": True
    }
    
    # 1. OLLAMA (Local)
    if provider == "ollama":
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.LLM_BASE_URL}/api/show",
                    json={"name": model_name},
                    timeout=2.0
                )
                if response.status_code == 200:
                    data = response.json()
                    model_caps = data.get("capabilities", [])
                    if "vision" in model_caps:
                        caps["vision"] = True
                    
                    if not model_caps:
                        m = model_name.lower()
                        if any(x in m for x in ["llava", "moondream", "bakllava", "vision", "gemma3", "gemma4"]):
                            caps["vision"] = True
        except Exception as e:
            logger.error(f"Error fetching Ollama capabilities: {e}")

    # 1b. OLLAMA CLOUD
    elif provider == "ollama_cloud":
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
                response = await client.post(
                    "https://api.ollama.com/api/show",
                    json={"name": model_name},
                    headers=headers,
                    timeout=3.0
                )
                if response.status_code == 200:
                    data = response.json()
                    model_caps = data.get("capabilities", [])
                    if "vision" in model_caps:
                        caps["vision"] = True
        except Exception as e:
            logger.warning(f"Error fetching Ollama Cloud capabilities: {e}")
            # Fallback sur le nom pour le cloud aussi
            if "vision" in model_name.lower() or "vl" in model_name.lower():
                caps["vision"] = True

    # 2. OPENROUTER
    elif provider == "openrouter":
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://openrouter.ai/api/v1/models", timeout=5.0)
                if response.status_code == 200:
                    models_data = response.json().get("data", [])
                    target = next((m for m in models_data if m["id"] == model_name), None)
                    if target:
                        arch = target.get("architecture", {})
                        if "image" in arch.get("input_modalities", []):
                            caps["vision"] = True
        except Exception as e:
            logger.error(f"Error fetching OpenRouter capabilities: {e}")

    # 3. GEMINI
    elif provider == "gemini":
        caps["vision"] = True
        caps["search"] = True

    # 4. GROQ
    elif provider == "groq":
        if "vision" in model_name.lower():
            caps["vision"] = True

    # Web Search global
    if settings.ENABLE_WEB_SEARCH:
        caps["search"] = True

    MODEL_CAPS_CACHE[cache_key] = caps
    return caps

async def fetch_model_context_limit(model_name: str) -> int:
    """Retourne la limite de contexte d'un modèle (en caractères)."""
    if model_name in MODEL_LIMITS_CACHE:
        return MODEL_LIMITS_CACHE[model_name]
    
    # 0. Hardcoded limits pour les modèles Cloud connus (en tokens * 4 pour les caractères)
    cloud_limits = {
        "llama-3.3-70b-versatile": 128000 * 4,
        "llama-3.1-70b-versatile": 128000 * 4,
        "llama-3.1-8b-instant": 128000 * 4,
        "mixtral-8x7b-32768": 32768 * 4,
        "gemini-1.5-flash": 1000000 * 4,
        "gemini-1.5-pro": 2000000 * 4,
        "gpt-4o": 128000 * 4,
        "gpt-4o-mini": 128000 * 4,
        "claude-3-5-sonnet": 200000 * 4,
    }
    
    # Mapping partiel pour OpenRouter/Groq
    m_lower = model_name.lower()
    if "llama-3.3-70b" in m_lower: return 128000 * 4
    if "llama-3.1" in m_lower: return 128000 * 4
    if "mixtral-8x7b" in m_lower: return 32768 * 4
    if "gemini-1.5" in m_lower: return 1000000 * 4
    if "gpt-4o" in m_lower: return 128000 * 4
    if "claude-3" in m_lower: return 200000 * 4

    default_limit = 32000 # Fallback si non trouvé
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.LLM_BASE_URL}/api/show", 
                json={"name": model_name},
                timeout=2.0
            )
            if response.status_code == 200:
                data = response.json()
                
                # 1. On cherche d'abord dans model_info (plus précis)
                model_info = data.get("model_info", {})
                for key, value in model_info.items():
                    if "context_length" in key:
                        limit = int(value)
                        # Conversion tokens -> caractères (approx x4)
                        final_limit = limit * 4 if limit < 1000000 else limit
                        MODEL_LIMITS_CACHE[model_name] = final_limit
                        return final_limit

                # 2. On cherche dans les paramètres (Modelfile)
                params = data.get("parameters", "")
                if "num_ctx" in params:
                    match = re.search(r"num_ctx\s+(\d+)", params)
                    if match:
                        limit = int(match.group(1))
                        final_limit = limit * 4 if limit < 1000000 else limit
                        MODEL_LIMITS_CACHE[model_name] = final_limit
                        return final_limit
                
                MODEL_LIMITS_CACHE[model_name] = default_limit
                return default_limit
    except Exception as e:
        logger.error(f"Error fetching model limit for {model_name}: {e}")
    
    return default_limit

# Cache pour les listes de modèles
AVAILABLE_MODELS_CACHE = {}

async def get_available_models(provider: str = "ollama", api_key: Optional[str] = None, custom_url: Optional[str] = None) -> List[str]:
    """Récupère la liste des modèles disponibles pour un provider donné."""
    cache_key = f"list:{provider}:{custom_url or 'default'}"
    if cache_key in AVAILABLE_MODELS_CACHE:
        return AVAILABLE_MODELS_CACHE[cache_key]
    
    models = []
    try:
        async with httpx.AsyncClient() as client:
            # 1. OLLAMA (Local)
            if provider == "ollama":
                response = await client.get(f"{settings.LLM_BASE_URL}/api/tags", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    models = [m["name"] for m in data.get("models", []) if "embed" not in m["name"]]
            
            # 1c. CUSTOM OPENAI-COMPATIBLE SERVER (vLLM, LM Studio, etc.)
            elif provider == "vllm":
                url = custom_url or "http://localhost:8000/v1"
                # On s'assure que l'URL finit par /v1/models ou /models
                if not url.endswith("/models"):
                    fetch_url = f"{url.rstrip('/')}/models"
                else:
                    fetch_url = url
                
                headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
                response = await client.get(fetch_url, headers=headers, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    models = [m["id"] for m in data.get("data", [])]
            
            # 1b. OLLAMA CLOUD
            elif provider == "ollama_cloud":
                headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
                response = await client.get("https://api.ollama.com/api/tags", headers=headers, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    models = [m["name"] for m in data.get("models", []) if "embed" not in m["name"]]

            # 2. OPENROUTER
            elif provider == "openrouter":
                response = await client.get("https://openrouter.ai/api/v1/models", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    models = [m["id"] for m in data.get("data", [])]
            
            # 3. GROQ
            elif provider == "groq":
                key = api_key or getattr(settings, "GROQ_API_KEY", None)
                if key:
                    headers = {"Authorization": f"Bearer {key}"}
                    response = await client.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=5.0)
                    if response.status_code == 200:
                        data = response.json()
                        models = [m["id"] for m in data.get("data", [])]

    except Exception as e:
        logger.error(f"Error fetching models for {provider}: {e}")
    
    if models:
        models.sort()
        AVAILABLE_MODELS_CACHE[cache_key] = models
        return models
    
    # Fallback sur les modèles par défaut si erreur ou liste vide
    default_models = {
        "ollama": [settings.clean_orchestrator_model],
        "ollama_cloud": ["llama3.2-vision:cloud", "qwen2.5-vl:cloud"],
        "groq": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
        "openrouter": ["meta-llama/llama-3-8b-instruct"]
    }
    return default_models.get(provider, [])
