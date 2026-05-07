import psutil
import platform
import subprocess
import os
from typing import Dict, Any

class SystemDiscoveryService:
    def get_system_info(self) -> Dict[str, Any]:
        """Détecte les ressources système pour recommander des modèles."""
        mem = psutil.virtual_memory()
        ram_gb = round(mem.total / (1024**3), 2)
        available_ram_gb = round(mem.available / (1024**3), 2)
        
        info = {
            "os": platform.system(),
            "cpu": platform.processor(),
            "ram_gb": ram_gb,
            "available_ram_gb": available_ram_gb,
            "gpu": self._detect_gpu(),
            "ollama_installed": self._check_ollama(),
            "installed_models": self._get_installed_models()
        }
        
        # Recommandations (basées sur la RAM disponible ou VRAM)
        info["recommendations"] = self._get_recommendations(available_ram_gb, info["gpu"])
        
        return info

    def _get_installed_models(self) -> list:
        """Liste les modèles Ollama déjà téléchargés."""
        try:
            res = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if res.returncode == 0:
                # Parse lines, skip header
                lines = res.stdout.strip().split('\n')[1:]
                return [line.split()[0] for line in lines if line]
        except:
            pass
        return []

    def _detect_gpu(self) -> Dict[str, Any]:
        """Détecte la présence d'un GPU (NVIDIA ou Apple Silicon)."""
        gpu_info = {"type": "CPU only", "vram_gb": 0}
        
        try:
            if platform.system() == "Darwin": # macOS
                gpu_info["type"] = "Apple Silicon"
                gpu_info["vram_gb"] = round(psutil.virtual_memory().total / (1024**3) * 0.75, 2)
            else:
                try:
                    import torch
                    if torch.cuda.is_available():
                        vram = torch.cuda.get_device_properties(0).total_memory
                        gpu_info["type"] = torch.cuda.get_device_name(0)
                        gpu_info["vram_gb"] = round(vram / (1024**3), 2)
                except:
                    # Fallback nvidia-smi
                    try:
                        res = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"], text=True)
                        vram = int(res.strip().split('\n')[0])
                        gpu_info["type"] = "NVIDIA GPU"
                        gpu_info["vram_gb"] = round(vram / 1024, 2)
                    except:
                        pass
        except:
            pass
            
        return gpu_info

    def _check_ollama(self) -> bool:
        """Vérifie si Ollama est installé et accessible."""
        try:
            subprocess.run(["ollama", "--version"], capture_output=True, check=True)
            return True
        except:
            return False

    def _get_recommendations(self, ram_gb: float, gpu: Dict[str, Any]) -> Dict[str, Any]:
        """Suggère des modèles basés sur la VRAM/RAM par Persona, en privilégiant l'existant."""
        total_memory = gpu["vram_gb"] if gpu["vram_gb"] > 0 else ram_gb
        installed = self._get_installed_models()
        
        tier = "low"
        if total_memory >= 48: tier = "high"
        elif total_memory >= 12: tier = "mid"
        
        def pick_best(default: str, family: str = None) -> str:
            # Si le défaut est déjà là, super
            if default in installed: return default
            # Si on a un modèle de la même famille (ex: gemma4)
            if family:
                matching = [m for m in installed if m.startswith(family)]
                if matching: return matching[0]
            return default

        personas = {
            "generalist": {
                "id": "generalist",
                "title": "Généraliste",
                "icon": "🧭",
                "description": "Polyvalent, rapide et efficace pour le quotidien.",
                "model": pick_best("phi3:mini" if tier == "low" else ("llama3.1:8b" if tier == "mid" else "llama3.1:70b"), "llama3.1")
            },
            "coder": {
                "id": "coder",
                "title": "Expert Coder",
                "icon": "💻",
                "description": "Spécialiste du refactoring et du debug profond.",
                "model": pick_best("qwen2.5-coder:3b" if tier == "low" else ("codestral:latest" if tier == "mid" else "deepseek-coder-v2:latest"), "qwen2.5-coder")
            },
            "analyst": {
                "id": "analyst",
                "title": "Data Scientist",
                "icon": "📊",
                "description": "Expert en logique, SQL et manipulation de données.",
                "model": pick_best("gemma2:2b" if tier == "low" else ("gemma2:9b" if tier == "mid" else "gemma2:27b"), "gemma")
            },
            "writer": {
                "id": "writer",
                "title": "Tech Writer",
                "icon": "📚",
                "description": "Clarté rédactionnelle et documentation multilingue.",
                "model": pick_best("phi3:mini" if tier == "low" else ("mistral-nemo:latest" if tier == "mid" else "command-r:latest"), "mistral")
            },
            "architect": {
                "id": "architect",
                "title": "System Architect",
                "icon": "🏗️",
                "description": "Vision globale et design patterns complexes.",
                "model": pick_best("mistral:7b" if tier == "low" else ("command-r:latest" if tier == "mid" else "command-r-plus:latest"), "command-r")
            }
        }
        
        profiles = []
        
        # 1. Ajout du "System Hero" si des modèles sont déjà là
        if installed:
            # On cherche un modèle costaud dans la liste (ex: 70b, 26b, 27b, 8b)
            best_installed = installed[0]
            for m in installed:
                if any(size in m.lower() for size in ["70b", "26b", "27b", "8b", "7b"]):
                    best_installed = m
                    break
            
            profiles.append({
                "id": "hero",
                "title": "Config Actuelle",
                "icon": "✨",
                "description": f"Utilise ton modèle '{best_installed}' déjà prêt sur ton système.",
                "model": best_installed,
                "is_hero": True
            })

        # 2. Ajout des personas standards
        profiles.extend(list(personas.values()))
        
        return {
            "tier": tier,
            "total_memory_gb": total_memory,
            "profiles": profiles
        }

system_discovery = SystemDiscoveryService()
