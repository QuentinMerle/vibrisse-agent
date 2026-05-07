import logging
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_llm(
    provider: str = "ollama",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.0,
    streaming: bool = True,
    role: Optional[str] = None
):
    """
    Factory pour instancier dynamiquement le bon client LLM.
    Priorise les réglages fournis par l'utilisateur (via le frontend).
    """
    
    # 1. Sélection du modèle selon le rôle (si non fourni explicitement)
    if not model and role:
        role_map = {
            "supervisor": settings.LLM_MODEL_ORCHESTRATOR,
            "coder": settings.LLM_MODEL_CODER,
            "writer": settings.LLM_MODEL_WRITER,
            "architect": settings.LLM_MODEL_ARCHITECT,
            "reviewer": settings.LLM_MODEL_REVIEWER
        }
        model = role_map.get(role, settings.LLM_MODEL)

    # 2. Nettoyage du nom du modèle (retrait du préfixe provider si présent)
    if model and "/" in model:
        model_name = model.split("/")[-1]
    else:
        model_name = model or settings.clean_orchestrator_model

    # 3. OLLAMA (Défaut / Local)
    if provider == "ollama":
        print(f"--- 🧠 LLM OLLAMA: Sending request to {model_name} (Base: {settings.LLM_BASE_URL}) ---", flush=True)
        return ChatOpenAI(
            model=model_name,
            base_url=f"{settings.LLM_BASE_URL}/v1",
            api_key="ollama", 
            temperature=temperature,
            streaming=streaming
        )

    # 4. OLLAMA CLOUD
    elif provider == "ollama_cloud":
        key = api_key
        if not key:
            raise ValueError("Clé API Ollama Cloud manquante.")
        
        logger.info(f"--- 🧠 LLM FACTORY : Instanciation OLLAMA CLOUD ({model_name}) ---")
        
        # Robustesse : si le modèle ressemble à un tag local Ollama (sans suffixe :cloud ou autre connu)
        if ":" in model_name and not model_name.endswith(":cloud"):
             logger.warning(f"Modèle '{model_name}' semble être un tag local. Fallback sur llama3.2-vision:cloud pour Ollama Cloud.")
             model_name = "llama3.2-vision:cloud"

        return ChatOpenAI(
            model=model_name,
            base_url="https://api.ollama.com/v1",
            api_key=key,
            temperature=temperature,
            streaming=streaming
        )

    # 5. GROQ (Connecteur Officiel)
    elif provider == "groq":
        key = api_key or getattr(settings, "GROQ_API_KEY", None)
        
        # Sécurité JS : parfois les headers arrivent avec la string "undefined" ou "null"
        if not key or key in ["undefined", "null", ""]:
            raise ValueError("Clé API Groq manquante. Veuillez la configurer dans les réglages.")
        
        logger.info(f"--- 🧠 LLM FACTORY : Instanciation GROQ ({model_name}) ---")
        
        # Robustesse : si le modèle ressemble à un tag Ollama (ex: gemma4:e4b), 
        # on évite d'envoyer ça à Groq qui va 404.
        if ":" in model_name:
            logger.warning(f"Modèle '{model_name}' semble être un tag Ollama. Fallback sur llama-3.3-70b-versatile pour Groq.")
            model_name = "llama-3.3-70b-versatile"

        return ChatGroq(
            model=model_name,
            api_key=key,
            temperature=temperature,
            streaming=streaming
        )

    # 6. OPENROUTER
    elif provider == "openrouter":
        key = api_key or getattr(settings, "OPENROUTER_API_KEY", None)
        if not key:
            raise ValueError("Clé API OpenRouter manquante.")
        
        logger.info(f"--- 🧠 LLM FACTORY : Instanciation OPENROUTER ({model_name}) ---")
        
        # Robustesse : si le modèle ressemble à un tag Ollama sans provider
        if ":" in model_name and "/" not in model_name:
            logger.warning(f"Modèle '{model_name}' semble être un tag Ollama. Fallback sur llama-3.1-8b pour OpenRouter.")
            model_name = "meta-llama/llama-3.1-8b-instruct"

        return ChatOpenAI(
            model=model_name,
            base_url="https://openrouter.ai/api/v1",
            api_key=key,
            temperature=temperature,
            streaming=streaming
        )

    # Fallback
    logger.warning(f"Provider inconnu '{provider}', fallback sur Ollama.")
    return ChatOpenAI(
        model=settings.clean_orchestrator_model,
        base_url=f"{settings.LLM_BASE_URL}/v1",
        api_key="ollama",
        temperature=temperature,
        streaming=streaming
    )

