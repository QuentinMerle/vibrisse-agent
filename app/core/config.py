# app/core/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    # Core Config
    APP_NAME: str = "VibrisseAgent-API"
    APP_DEBUG: bool = False
    SECURITY_SCRUBBING_ENABLED: bool = True
    TARGET_PROJECT_PATH: str = "." # Dossier à analyser (ex: data/source_code)
    
    def __init__(self, **values):
        super().__init__(**values)
        self._load_session_if_exists()

    def _load_session_if_exists(self):
        """Tente de restaurer le dernier projet utilisé."""
        try:
            # Import local pour éviter les imports circulaires
            from app.services.core.session_service import session_service
            session = session_service.load_session()
            if session.get("last_project_path"):
                self.TARGET_PROJECT_PATH = session["last_project_path"]
                print(f"--- 📂 SESSION: Restored project path: {self.TARGET_PROJECT_PATH} ---", flush=True)
            if session.get("last_manifest"):
                self.PROJECT_MANIFEST = session["last_manifest"]
                print(f"--- 🧠 SESSION: Restored manifest from cache ---", flush=True)
        except Exception:
            pass # Silencieux au démarrage
    
    # LLM Config
    LLM_PROVIDER: str = "ollama" # ollama, openai, google
    LLM_MODEL: str = "ollama/gemma4:e2b"  # Modèle par défaut
    LLM_MODEL_ORCHESTRATOR: str = "ollama/gemma4:e2b"
    LLM_MODEL_CODER: str = "ollama/gemma4:e2b"
    LLM_MODEL_WRITER: str = "ollama/gemma4:e2b"
    LLM_MODEL_ARCHITECT: str = "ollama/gemma4:e2b"
    LLM_MODEL_REVIEWER: str = "ollama/gemma4:e2b"
    LLM_BASE_URL: str = "http://localhost:11434"
    LLM_TEMPERATURE: float = 0.0
    
    # RAG Config
    CONTEXT_COMPRESSION_ENABLED: bool = True
    MAX_CONTEXT_CHUNKS: int = 5
    CONTEXT_LIMIT_CHARS: int = 32000
    
    # Evaluation Config (Ragas)
    RAGAS_MODEL: str = "llama3" # Recommandé 8B+ pour le juge
    RAGAS_EMBEDDING_MODEL: str = "nomic-embed-text"

    # Feature Flags (Outils Dynamiques) — valeurs par défaut alignées sur .env
    ENABLE_WEB_SEARCH: bool = True
    ENABLE_VISION: bool = True
    ENABLE_GITHUB: bool = False
    ENABLE_EXPERT_REVIEW: bool = True
    
    # API Keys (pour outils externes si besoin)
    GITHUB_TOKEN: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None

    # Project Manifest (Auto-generated on startup)
    PROJECT_MANIFEST: str = ""

    # LangSmith
    LANGCHAIN_TRACING_V2: Optional[str] = None
    LANGCHAIN_ENDPOINT: Optional[str] = None
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: Optional[str] = None

    # Cloud Providers
    GOOGLE_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    
    model_config = SettingsConfigDict(
        # Priorité : .env.native > .env
        env_file=(
            ".env.native" if os.path.exists(".env.native") else ".env"
        ),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def clean_orchestrator_model(self) -> str:
        """Retourne le nom du modèle sans le préfixe du provider (ex: gemma4:e2b au lieu de ollama/gemma4:e2b)"""
        return self.LLM_MODEL_ORCHESTRATOR.split("/")[-1]

    @property
    def clean_coder_model(self) -> str:
        return self.LLM_MODEL_CODER.split("/")[-1]

    def get_project_profile(self) -> str:
        """Détecte les technos du projet pour injecter du contexte aux agents."""
        # Si un manifeste a été généré (digéré par LLM), on l'utilise en priorité
        if self.PROJECT_MANIFEST:
            return self.PROJECT_MANIFEST
            
        from pathlib import Path
        root = Path(self.TARGET_PROJECT_PATH)
        profile = []
        
        # Fallback si pas de manifeste
        if self.ENABLE_WEB_SEARCH: profile.append("SEARCH")
        if self.ENABLE_VISION: profile.append("VISION")
        # Suppression de l'injection du modèle pour éviter la confusion d'identité
        
        if (root / "docker-compose.yml").exists():
            profile.append("DOCKER")
            
        return ", ".join(profile) if profile else "STACK STANDARD"

    async def load_manifest(self):
        """Initialise le manifeste au démarrage ou lors d'un changement de dossier."""
        from app.services.core.onboarding import onboarding_service
        from app.services.core.session_service import session_service
        
        # On passe le path cible au service d'onboarding
        target_path = Path(self.TARGET_PROJECT_PATH)
        self.PROJECT_MANIFEST = await onboarding_service.scan_project(root_path=target_path)
        
        # Sauvegarde en session pour le prochain redémarrage
        session_service.save_session(
            project_path=str(target_path),
            manifest=self.PROJECT_MANIFEST,
            onboarded=True
        )

settings = Settings()