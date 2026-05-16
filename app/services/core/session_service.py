# app/services/core/session_service.py
import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class SessionService:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data"
        self.session_file = self.data_dir / "session.json"
        self.key_file = self.data_dir / ".secret_key"
        self._ensure_data_dir()
        self.fernet = self._init_fernet()

    def _ensure_data_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def _init_fernet(self) -> Fernet:
        """Initialise le moteur de chiffrement avec une clé locale persistante."""
        if not self.key_file.exists():
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
        else:
            with open(self.key_file, "rb") as f:
                key = f.read()
        return Fernet(key)

    def _encrypt_data(self, data: Dict[str, Any]) -> str:
        """Chiffre un dictionnaire en chaîne de caractères."""
        json_data = json.dumps(data).encode()
        return self.fernet.encrypt(json_data).decode()

    def _decrypt_data(self, encrypted_str: str) -> Dict[str, Any]:
        """Déchiffre une chaîne en dictionnaire."""
        try:
            decrypted_data = self.fernet.decrypt(encrypted_str.encode())
            return json.loads(decrypted_data.decode())
        except Exception as e:
            logger.error(f"Failed to decrypt session settings: {e}")
            return {}

    def save_session(self, project_path: Optional[str] = None, manifest: Optional[str] = None, onboarded: Optional[bool] = None, settings: Optional[Dict[str, Any]] = None):
        """Sauvegarde les informations de session et les paramètres globaux (chiffrés)."""
        current = self.load_session()
        
        new_settings = settings if settings is not None else current.get("settings", {})
        
        session_data = {
            "last_project_path": project_path if project_path is not None else current.get("last_project_path"),
            "last_manifest": manifest if manifest is not None else current.get("last_manifest"),
            "onboarded": onboarded if onboarded is not None else current.get("onboarded", True),
            "settings": self._encrypt_data(new_settings) if new_settings else None
        }
        
        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=4, ensure_ascii=False)
            logger.info(f"--- 💾 SESSION: Saved to {self.session_file} (Encrypted) ---")
        except Exception as e:
            logger.error(f"⚠️ SESSION: Failed to save ({e})")

    def load_session(self) -> Dict[str, Any]:
        """Charge les informations de session et déchiffre les paramètres."""
        if not self.session_file.exists():
            return {}
        
        try:
            with open(self.session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Déchiffrement des settings si présents
                encrypted_settings = data.get("settings")
                if isinstance(encrypted_settings, str):
                    data["settings"] = self._decrypt_data(encrypted_settings)
                elif isinstance(encrypted_settings, dict):
                    # Migration: le format précédent était un dictionnaire en clair
                    logger.warning("Session legacy (clair) détectée. Migration vers format chiffré au prochain enregistrement.")
                    data["settings"] = encrypted_settings
                else:
                    data["settings"] = {}
                
                return data
        except Exception as e:
            logger.error(f"⚠️ SESSION: Failed to load ({e})")
            return {}

session_service = SessionService()
