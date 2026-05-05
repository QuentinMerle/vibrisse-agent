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

@tool
def write_file(filename: str, content: str):
    """Crée ou met à jour un fichier avec le contenu spécifié. Utile pour sauvegarder des articles, du code ou de la documentation."""
    from pathlib import Path
    try:
        # On s'assure que le chemin est relatif au projet cible
        from app.core.config import settings
        target_dir = Path(settings.TARGET_PROJECT_PATH).absolute()
        file_path = (target_dir / filename).absolute()
        
        # Sécurité : on empêche d'écrire en dehors du dossier projet
        if not str(file_path).startswith(str(target_dir)):
            return f"Erreur : Tentative d'écriture en dehors du dossier projet autorisé ({target_dir})."

        # Création des dossiers parents si besoin
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return f"Succès : Le fichier '{filename}' a été écrit avec succès ({len(content)} caractères)."
    except Exception as e:
        return f"Erreur lors de l'écriture du fichier : {str(e)}"

@tool
def list_dir(directory: str = "."):
    """Liste les fichiers et dossiers dans un répertoire spécifique. Utile pour comprendre la structure du projet."""
    from pathlib import Path
    try:
        from app.core.config import settings
        target_dir = Path(settings.TARGET_PROJECT_PATH).absolute()
        path = (target_dir / directory).absolute()
        
        if not str(path).startswith(str(target_dir)):
            return "Erreur : Accès hors du dossier projet interdit."
            
        if not path.exists():
            return f"Erreur : Le dossier '{directory}' n'existe pas."
            
        items = os.listdir(path)
        # On ignore les dossiers cachés et les trucs lourds
        items = [i for i in items if not i.startswith('.') and i != "node_modules" and i != "__pycache__"]
        
        return f"Contenu de {directory} :\n" + "\n".join(sorted(items))
    except Exception as e:
        return f"Erreur lors du listage : {str(e)}"

@tool
def read_file(filename: str):
    """Lit le contenu complet d'un fichier. À utiliser quand le RAG ne donne pas assez de détails sur un fichier spécifique."""
    from pathlib import Path
    try:
        from app.core.config import settings
        target_dir = Path(settings.TARGET_PROJECT_PATH).absolute()
        path = (target_dir / filename).absolute()
        
        if not str(path).startswith(str(target_dir)):
            return "Erreur : Accès hors du dossier projet interdit."
            
        if not path.is_file():
            return f"Erreur : '{filename}' n'est pas un fichier valide."
            
        with open(path, "r", encoding="utf-8") as f:
            content = f.read(5000) # Limite de sécurité pour le contexte
            if len(content) >= 5000:
                content += "\n... [Fichier tronqué à 5000 caractères]"
            return content
    except Exception as e:
        return f"Erreur lors de la lecture : {str(e)}"

@tool
def grep_search(pattern: str, directory: str = "."):
    """Cherche une chaîne de caractères ou un pattern dans les fichiers du projet. Idéal pour trouver des variables ou des appels de fonctions précis."""
    import subprocess
    from pathlib import Path
    try:
        from app.core.config import settings
        target_dir = Path(settings.TARGET_PROJECT_PATH).absolute()
        
        # On utilise grep -r (récursif), -l (juste les noms de fichiers) ou sans -l pour voir les lignes
        cmd = f"grep -rnI --exclude-dir={{node_modules,__pycache__,.git}} \"{pattern}\" {target_dir / directory}"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        output = result.stdout
        
        if not output:
            return f"Aucun résultat trouvé pour '{pattern}'."
            
        if len(output) > 3000:
            output = output[:3000] + "\n... [Trop de résultats, tronqué]"
            
        return output
    except Exception as e:
        return f"Erreur lors du grep : {str(e)}"
