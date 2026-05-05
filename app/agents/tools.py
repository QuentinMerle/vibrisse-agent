import os
from langchain_core.tools import tool
import subprocess
from app.core.config import settings

@tool
def web_search(query: str):
    """Recherche sur le web pour obtenir des informations actualisées (météo, news, etc.)."""
    tavily_key = settings.TAVILY_API_KEY
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key
        try:
            from langchain_tavily import TavilySearch
            search = TavilySearch(max_results=3)
            results = search.invoke(query)
            # Nouvelle API (≥0.1.0) retourne une string directement
            if isinstance(results, str):
                return results[:4000]
            # Ancienne API retournait une liste de dicts {"content": "..."}
            elif isinstance(results, list):
                clean_text = ""
                for i, res in enumerate(results):
                    snippet = res.get("content", str(res))[:1000]
                    clean_text += f"\n[Source {i+1}]: {snippet}\n"
                return clean_text
            else:
                return str(results)[:4000]
        except Exception as e:
            print(f"⚠️ Échec Tavily: {e}", flush=True)

    # Fallback sur DuckDuckGo (Gratuit, pas de clé)
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        search = DuckDuckGoSearchRun()
        result = search.invoke(query)
        return f"\n[Source Web (DuckDuckGo)]: {result[:3000]}\n"
    except Exception as e:
        return f"Erreur critique : Impossible d'accéder au web ({str(e)})"

@tool
def run_terminal_command(command: str):
    """Exécute une commande terminal pour obtenir des infos système (versions, fichiers, config, matériel) ou effectuer des actions. À utiliser en priorité pour toute question sur l'environnement local."""
    try:
        # Restriction de sécurité : commandes destructrices bloquées
        forbidden = ["rm -rf", "format", "mkfs", "> /dev/sda", "dd if=", ":(){ :|:& };:"]
        if any(f in command for f in forbidden):
            return "Erreur : Commande jugée dangereuse et bloquée par le système de sécurité."

        result = subprocess.run(
            command, shell=True, capture_output=True,
            text=True, timeout=30
        )
        output = result.stdout if result.stdout else result.stderr
        # Limite l'output pour ne pas saturer le contexte du LLM
        if len(output) > 3000:
            output = output[:3000] + "\n... [Output tronqué à 3000 chars]"
        return output if output else "Commande exécutée avec succès (pas de sortie)."
    except subprocess.TimeoutExpired:
        return "Erreur : La commande a dépassé le délai de 30 secondes."
    except Exception as e:
        return f"Erreur d'exécution : {str(e)}"
