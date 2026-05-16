import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class MappingService:
    """
    Génère une carte architecturale du projet (project_map.json).
    Aide les modèles à comprendre la structure globale sans lire tous les fichiers.
    """

    @staticmethod
    def generate_map(root_path: str) -> Dict[str, Any]:
        root = Path(root_path)
        project_map = {
            "name": root.name,
            "structure": {},
            "key_files": [],
            "stats": {
                "total_files": 0,
                "languages": {}
            }
        }

        ignore_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'dist', 'build', '.next'}
        valid_exts = {'.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.md', '.go', '.rs'}

        for path in root.rglob('*'):
            if any(part in ignore_dirs for part in path.parts):
                continue
            
            if path.is_file():
                project_map["stats"]["total_files"] += 1
                ext = path.suffix.lower()
                if ext:
                    project_map["stats"]["languages"][ext] = project_map["stats"]["languages"].get(ext, 0) + 1
                
                # Fichiers clés (racine ou config)
                if len(path.relative_to(root).parts) == 1 or path.name in ['package.json', 'requirements.txt', 'main.py']:
                    project_map["key_files"].append(str(path.relative_to(root)))

        # Sauvegarde persistante dans .vibrisse/
        vibrisse_dir = root / ".vibrisse"
        vibrisse_dir.mkdir(exist_ok=True)
        map_path = vibrisse_dir / "project_map.json"
        
        with open(map_path, "w", encoding="utf-8") as f:
            json.dump(project_map, f, indent=2)
            
        logger.info(f"🗺️ Architecture Map générée : {map_path}")
        return project_map

mapping_service = MappingService()
