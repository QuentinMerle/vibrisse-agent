import os
import re
from typing import List, Dict, Any
from app.core.config import settings
from app.agents.state import AgentState

def load_skill(name: str) -> str:
    """Charge une compétence depuis le dossier skills."""
    # Point to app/agents/skills/
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills", f"{name}.md")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"⚠️ Error loading skill {name}: {e}")
        return ""

async def get_active_tools():
    from app.agents.tools import web_search, run_terminal_command, write_file, list_dir, read_file, grep_search
    from app.services.mcp.mcp_client import mcp_manager
    tools = [run_terminal_command, write_file, list_dir, read_file, grep_search] # Outils locaux prioritaires
    if settings.ENABLE_WEB_SEARCH:
        tools.append(web_search)
        
    # Ajout dynamique des outils provenant de tous les serveurs MCP connectés
    for server_id in list(mcp_manager.sessions.keys()):
        try:
            mcp_tools = await mcp_manager.get_langchain_tools(server_id)
            tools.extend(mcp_tools)
            print(f"🔌 {len(mcp_tools)} outils chargés depuis le serveur MCP '{server_id}'", flush=True)
        except Exception as e:
            print(f"⚠️ Erreur lors de la récupération des outils MCP ({server_id}): {e}")
            
    return tools

def extract_thought(text: str) -> str:
    """Extrait le contenu entre les balises <thought> ou similaires."""
    patterns = [r"<thought>(.*?)</thought>", r"<think>(.*?)</think>", r"<thinking>(.*?)</thinking>"]
    for p in patterns:
        match = re.search(p, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""

def calculate_context_usage(state: AgentState) -> int:
    """Calcule la taille totale du contexte en caractères."""
    messages = state.get("messages", [])
    context = state.get("context", "")
    vision_desc = state.get("vision_description", "")
    
    total_chars = 0
    # 1. Messages (Historique)
    for m in messages:
        content = getattr(m, "content", "") or (m.get("content") if isinstance(m, dict) else "")
        if isinstance(content, str):
            total_chars += len(content)
        elif isinstance(content, list): # Support multimodal (Gemma/Vision)
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    total_chars += len(part.get("text", ""))
                    
    # 2. Contexte RAG
    if isinstance(context, str):
        total_chars += len(context)
    elif isinstance(context, list):
        total_chars += sum(len(str(c)) for c in context)
        
    # 3. Vision
    if vision_desc:
        total_chars += len(vision_desc)
        
    return total_chars

def get_project_context():
    profile = settings.get_project_profile()
    skill_code = load_skill("code_expert")
    return f"{skill_code}\n\n--- INFORMATIONS SUR LE PROJET ANALYSÉ ---\n{profile}\n"

def clean_mentions(text: str) -> str:
    """
    Remplace le format technique @[display](id) par l'ID réel (chemin du fichier) pour le LLM.
    Ex: @[App.jsx](/src/App.jsx) -> /src/App.jsx
    """
    if not isinstance(text, str):
        return text
    
    # On extrait l'ID (le deuxième groupe) et on déséchappe les parenthèses
    # Le trigger peut être @ ou /
    def replace_with_id(match):
        path = match.group(2)
        return path.replace('%28', '(').replace('%29', ')')
        
    return re.sub(r"[@/]\[(.*?)\]\((.*?)\)", replace_with_id, text)

def create_node(node_id: str, label: str, node_type: str, icon: str) -> dict:
    return {
        "id": node_id,
        "type": "custom",
        "data": {"label": label, "type": node_type, "icon": icon}
    }

def create_edge(source: str, target: str, animated: bool = True) -> dict:
    return {
        "id": f"e-{source}-{target}",
        "source": source,
        "target": target,
        "animated": animated
    }

