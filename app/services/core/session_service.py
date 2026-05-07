# app/services/core/session_service.py
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class SessionService:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data"
        self.session_file = self.data_dir / "session.json"
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def save_session(self, project_path: str, manifest: str, onboarded: bool = True):
        """Sauvegarde les informations de session."""
        session_data = {
            "last_project_path": project_path,
            "last_manifest": manifest,
            "onboarded": onboarded
        }
        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=4, ensure_ascii=False)
            print(f"--- 💾 SESSION: Saved to {self.session_file} ---", flush=True)
        except Exception as e:
            print(f"⚠️ SESSION: Failed to save ({e})", flush=True)

    def load_session(self) -> Dict[str, Any]:
        """Charge les informations de session."""
        if not self.session_file.exists():
            return {}
        
        try:
            with open(self.session_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ SESSION: Failed to load ({e})", flush=True)
            return {}

session_service = SessionService()
