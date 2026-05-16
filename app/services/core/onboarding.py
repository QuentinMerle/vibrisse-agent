# app/services/onboarding.py
import os
from pathlib import Path
from typing import Dict, List, Optional
from app.services.core.mapping_service import mapping_service
import json

class OnboardingService:
    def __init__(self, root_path: Optional[Path] = None):
        self.root_path = root_path or Path(__file__).parent.parent.parent
        self.manifest: Dict[str, str] = {}

    async def scan_project(self, root_path: Optional[Path] = None) -> str:
        """Scanne le projet pour générer un manifeste condensé et digéré par LLM."""
        if root_path:
            self.root_path = root_path
            
        print(f"--- 🔍 ONBOARDING: Scanning {self.root_path} ---", flush=True)
        
        # 1. Lecture des fichiers de contexte (README, CONTEXT)
        context_data = self._read_context_files()
        
        # 2. Détection technique (Stack)
        tech_stack = self._detect_tech_stack()
        
        # 2.5 Mapping Architectural (project_map.json)
        print(f"--- 🗺️ ONBOARDING: Mapping architecture ---", flush=True)
        mapping_service.generate_map(str(self.root_path))
        
        # 3. Digestion par LLM (Nouvelle étape !)
        print(f"--- 🧠 ONBOARDING: Digesting documentation with LLM ---", flush=True)
        digested_content = await self._summarize_with_llm(context_data, tech_stack)
        
        # 4. Construction du manifeste final
        manifest_lines = [
            "=== PROJECT MANIFEST (Digested) ===",
            digested_content,
            "===================================="
        ]
        
        return "\n".join(manifest_lines)

    async def _summarize_with_llm(self, context_data: Dict[str, str], tech_stack: List[str]) -> str:
        """Utilise un modèle rapide pour transformer le bruit du README en instructions claires."""
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage
        from app.core.config import settings
        
        # On utilise le modèle orchestrateur (souvent plus rapide/léger)
        llm = ChatOpenAI(
            model=settings.LLM_MODEL_ORCHESTRATOR.replace("ollama/", ""),
            base_url=f"{settings.LLM_BASE_URL}/v1",
            api_key="ollama",
            temperature=0
        )
        
        raw_text = context_data.get('description', '')
        prompt = (
            "You are a project onboarding expert. Your mission is to transform raw documentation "
            "into a structured manifest for another AI agent.\n\n"
            "RAW DOCUMENTATION :\n"
            f"{raw_text}\n\n"
            f"DETECTED STACK : {', '.join(tech_stack)}\n\n"
            "Generate a condensed manifest (max 10 lines) with:\n"
            "1. PROJECT NAME\n"
            "2. CLIENT & CONTEXT\n"
            "3. TECHNICAL STACK (be precise)\n"
            "4. MAIN GOAL\n"
            "5. KEY CODING RULES (if found)\n\n"
            "Respond ONLY with the structured manifest."
        )
        
        try:
            response = await llm.ainvoke([
                SystemMessage(content="You are an efficient technical assistant."),
                HumanMessage(content=prompt)
            ])
            return response.content
        except Exception as e:
            print(f"⚠️ ONBOARDING: LLM Digestion failed ({e}), using fallback.", flush=True)
            return f"Project: {context_data.get('name')}\nStack: {', '.join(tech_stack)}\n(Full digestion failed)"

    def _read_context_files(self) -> Dict[str, str]:
        data = {
            "name": "Project Inconnu",
            "client": "Analyse Automatique",
            "description": "",
            "rules": ""
        }
        
        # 1. Recherche directe à la racine
        context_path = self.root_path / "CONTEXT.md"
        readme_path = self.root_path / "README.md"
        
        files_to_read = []
        if context_path.exists():
            files_to_read.append(context_path)
        if readme_path.exists():
            files_to_read.append(readme_path)
            
        # 2. Si rien à la racine, on cherche dans les sous-dossiers immédiats
        if not files_to_read:
            for subpath in self.root_path.iterdir():
                if subpath.is_dir() and not subpath.name.startswith('.'):
                    sub_readme = subpath / "README.md"
                    sub_context = subpath / "CONTEXT.md"
                    if sub_context.exists(): files_to_read.append(sub_context)
                    if sub_readme.exists(): files_to_read.append(sub_readme)
                    if files_to_read: break
            
        # 3. FALLBACK : Si toujours rien, on génère un inventaire de la structure
        if not files_to_read:
            print(f"--- 📂 ONBOARDING: No documentation found. Generating structure inventory... ---", flush=True)
            data["description"] = self._generate_folder_inventory()
            return data
            
        for path in files_to_read:
            try:
                content = path.read_text(encoding="utf-8")
                data["description"] += f"\n--- Source: {path.relative_to(self.root_path)} ---\n"
                data["description"] += content[:3000]
                if "CONTEXT.md" in path.name: break
            except Exception as e:
                print(f"⚠️ ONBOARDING: Error reading {path}: {e}")
            
        return data

    def _generate_folder_inventory(self) -> str:
        """Crée une signature textuelle du dossier pour que le LLM déduise l'activité."""
        inventory = ["INVENTAIRE DE STRUCTURE (No README found):"]
        extensions = set()
        file_count = 0
        
        try:
            for root, dirs, files in os.walk(self.root_path):
                # On ignore les dossiers cachés et techniques
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.venv', '.git']]
                
                rel_path = os.path.relpath(root, self.root_path)
                level = rel_path.count(os.sep)
                indent = ' ' * 4 * level
                
                if rel_path != '.':
                    inventory.append(f"{indent}📁 {os.path.basename(root)}/")
                
                for f in files[:10]: # On limite pour pas exploser le prompt
                    if f.startswith('.'): continue
                    inventory.append(f"{indent}    📄 {f}")
                    if '.' in f:
                        extensions.add(f.split('.')[-1].lower())
                    file_count += 1
                
                if len(inventory) > 50: # On s'arrête si le dossier est trop gros
                    inventory.append("... (trop de fichiers pour l'aperçu)")
                    break
                    
        except Exception as e:
            return f"Erreur lors du scan du dossier : {e}"
            
        res = "\n".join(inventory)
        res += f"\n\nEXTENSIONS DÉTECTÉES : {', '.join(extensions)}"
        res += f"\nTOTAL ESTIMÉ : {file_count}+ fichiers."
        return res

    def _detect_tech_stack(self) -> List[str]:
        stack = []
        
        # Heuristiques
        indicators = {
            "package.json": "Node/JS",
            "tsconfig.json": "TypeScript",
            "tailwind.config.js": "TailwindCSS",
            "tailwind.config.ts": "TailwindCSS",
            "pyproject.toml": "Python (Poetry/Build)",
            "requirements.txt": "Python (Pip)",
            "docker-compose.yml": "Docker",
            "Dockerfile": "Docker",
            "next.config.js": "Next.js",
            "vite.config.js": "Vite",
            "app/main.py": "FastAPI/Python"
        }
        
        # Scan racine
        for file, label in indicators.items():
            if (self.root_path / file).exists():
                if label not in stack:
                    stack.append(label)
        
        # Scan frontend subdirectory if exists
        frontend_path = self.root_path / "frontend"
        if frontend_path.exists() and frontend_path.is_dir():
            for file, label in indicators.items():
                if (frontend_path / file).exists():
                    if label not in stack:
                        stack.append(label)
                    
        return stack

onboarding_service = OnboardingService()
