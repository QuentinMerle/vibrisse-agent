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
    streaming: bool = True
):
    """
    Factory pour instancier dynamiquement le bon client LLM.
    Priorise les réglages fournis par l'utilisateur (via le frontend).
    """
    
    # 1. OLLAMA (Défaut / Local)
    if provider == "ollama":
        model_name = model or settings.clean_orchestrator_model
        logger.info(f"--- 🧠 LLM FACTORY : Instanciation OLLAMA ({model_name}) ---")
        return ChatOpenAI(
            model=model_name,
            base_url=f"{settings.LLM_BASE_URL}/v1",
            api_key="ollama", # Requis par le SDK mais ignoré par Ollama
            temperature=temperature,
            streaming=streaming
        )

    # 2. OLLAMA CLOUD
    elif provider == "ollama_cloud":
        model_name = model or "llama3.2-vision"
        key = api_key
        if not key:
            raise ValueError("Clé API Ollama Cloud manquante.")
        
        logger.info(f"--- 🧠 LLM FACTORY : Instanciation OLLAMA CLOUD ({model_name}) ---")
        return ChatOpenAI(
            model=model_name,
            base_url="https://api.ollama.com/v1",
            api_key=key,
            temperature=temperature,
            streaming=streaming
        )

    # 3. GROQ (Connecteur Officiel)
    elif provider == "groq":
        model_name = model if model and ":" not in model else "llama-3.3-70b-versatile"
        key = api_key or getattr(settings, "GROQ_API_KEY", None)
        
        # Sécurité JS : parfois les headers arrivent avec la string "undefined" ou "null"
        if not key or key in ["undefined", "null", ""]:
            raise ValueError("Clé API Groq manquante. Veuillez la configurer dans les réglages.")
        
        logger.info(f"--- 🧠 LLM FACTORY : Instanciation GROQ ({model_name}) ---")
        return ChatGroq(
            model=model_name,
            api_key=key,
            temperature=temperature,
            streaming=streaming
        )

    # 4. OPENROUTER
    elif provider == "openrouter":
        model_name = model if model and ":" not in model else "meta-llama/llama-3-8b-instruct"
        key = api_key or getattr(settings, "OPENROUTER_API_KEY", None)
        if not key:
            raise ValueError("Clé API OpenRouter manquante.")
        
        logger.info(f"--- 🧠 LLM FACTORY : Instanciation OPENROUTER ({model_name}) ---")
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

