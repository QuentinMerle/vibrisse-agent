import logging
import re
from pathlib import Path
from typing import List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class GhostService:
    """
    Service gérant le 'Ghost Mode' (Directives In-File).
    Détecte les tags @vibrisse et orchestre les modifications automatiques.
    """
    
    GHOST_TAG_REGEX = r"@vibrisse\s*:?\s*(.*)"
    processing_files = set() # Empêche les boucles infinies du Watchdog
    
    @classmethod
    def scan_file(cls, file_path: str) -> List[str]:
        """Scanne un fichier pour trouver des directives @vibrisse."""
        if file_path in cls.processing_files:
            return []
            
        try:
            content = Path(file_path).read_text(encoding='utf-8')
            # On ne prend que les lignes qui contiennent le tag et qui sont des commentaires
            # (Heuristique simple : contient @vibrisse et n'est pas dans le lock)
            return re.findall(cls.GHOST_TAG_REGEX, content, re.IGNORECASE)
        except Exception as e:
            logger.error(f"Erreur scan Ghost Mode ({file_path}): {e}")
            return []

    @classmethod
    async def process_directives(cls, file_path: str, directives: List[str]):
        """
        Traite les directives trouvées dans un fichier.
        Lance une tâche d'agent en arrière-plan pour chaque instruction.
        """
        if file_path in cls.processing_files:
            return

        for directive in directives:
            if not directive.strip() or "✅" in directive or "DONE" in directive.upper():
                continue
                
            cls.processing_files.add(file_path)
            try:
                logger.info(f"👻 Ghost Mode activé : '{directive}' dans {file_path}")
                await cls._execute_ghost_task(file_path, directive)
            finally:
                # On laisse un court délai avant de libérer le fichier pour que le Watchdog 
                # ignore la modification que nous venons de faire.
                import asyncio
                await asyncio.sleep(2.0)
                cls.processing_files.discard(file_path)

    @classmethod
    async def _execute_ghost_task(cls, file_path: str, instruction: str):
        """Exécute l'instruction de l'agent sur le fichier."""
        from app.services.llm.llm_factory import get_llm
        from app.agents.nodes.utils import load_skill, get_project_context
        from langchain_core.messages import SystemMessage, HumanMessage
        import os

        # 1. Préparation du contexte
        try:
            file_content = Path(file_path).read_text(encoding='utf-8')
        except:
            return

        project_ctx = get_project_context()
        skill = load_skill("code_expert")
        
        prompt = f"""
{skill}
{project_ctx}

Tu es en 'Ghost Mode'. Tu dois modifier le fichier suivant selon l'instruction fournie.
FICHIER: {file_path}
CONTENU ACTUEL:
```
{file_content}
```

INSTRUCTION: {instruction}

IMPORTANT: 
1. Ne modifie QUE ce qui est demandé.
2. TA RÉPONSE DOIT ÊTRE LE CONTENU COMPLET ET MODIFIÉ DU FICHIER.
3. SUPPRIME OU METS À JOUR LE TAG @vibrisse une fois terminé (ex: @vibrisse: ✅ {instruction}).
4. NE RESTE PAS BLOQUÉ DANS UNE BOUCLE.
5. RÉPONDS UNIQUEMENT AVEC LE CODE DU FICHIER, SANS TEXTE AVANT OU APRÈS.
"""

        llm = get_llm(role="coder", temperature=0.1)
        
        try:
            print(f"--- 👻 GHOST LLM CALL : {instruction} ---", flush=True)
            
            # On demande au LLM de ne générer QUE le code de remplacement pour la ligne du tag
            ghost_prompt = f"""
Tu es un assistant de programmation chirurgical. 
Un utilisateur a laissé une instruction dans un fichier sous forme de commentaire.
INSTRUCTION: {instruction}
CONTEXTE DU FICHIER:
```
{file_content}
```

REMPLACEMENT:
Génère UNIQUEMENT le bloc de code qui doit remplacer la ligne contenant le tag '@vibrisse'.
Ne renvoie pas tout le fichier. Ne mets pas de blabla. 
Renvoie uniquement le code prêt à être inséré.
"""
            response = await llm.ainvoke([
                SystemMessage(content="Tu es Vibrisse Ghost, expert en insertion chirurgicale de code."),
                HumanMessage(content=ghost_prompt)
            ])
            
            replacement_code = response.content.strip()
            
            # Nettoyage agressif des backticks et du formatage markdown
            if "```" in replacement_code:
                # On cherche d'abord un bloc de code
                match = re.search(r"```(?:\w+)?\n?(.*?)\n?```", replacement_code, re.DOTALL)
                if match:
                    replacement_code = match.group(1).strip()
            
            # On enlève aussi les backticks simples s'ils entourent tout le code
            replacement_code = replacement_code.strip('`').strip()

            if replacement_code:
                # On remplace la ligne du tag par le nouveau code
                # On cherche la ligne qui contient @vibrisse et l'instruction
                lines = file_content.splitlines()
                new_lines = []
                for line in lines:
                    if "@vibrisse" in line and instruction in line:
                        new_lines.append(replacement_code)
                    else:
                        new_lines.append(line)
                
                Path(file_path).write_text("\n".join(new_lines), encoding='utf-8')
                print(f"--- 👻 GHOST SUCCESS : {file_path} mis à jour chirurgicalement ---", flush=True)
                
                # Enregistrement de la notification pour le frontend
                try:
                    import json, time, os
                    # Chemin absolu vers le dossier data à la racine du projet
                    base_dir = Path(__file__).resolve().parent.parent.parent.parent
                    notif_path = base_dir / "data" / "notifications.json"
                    
                    os.makedirs(notif_path.parent, exist_ok=True)
                    
                    notifs = []
                    if notif_path.exists():
                        try:
                            with open(notif_path, 'r', encoding='utf-8') as f:
                                notifs = json.load(f)
                        except: pass
                    
                    notifs.append({
                        "id": str(time.time()),
                        "type": "ghost",
                        "title": "Ghost Mode",
                        "message": f"Modification terminée dans {os.path.basename(file_path)}",
                        "file": file_path,
                        "timestamp": time.time(),
                        "read": False
                    })
                    
                    with open(notif_path, 'w', encoding='utf-8') as f:
                        json.dump(notifs[-10:], f)
                        
                    # --- NOTIFICATIONS NATIVES (Multi-plateforme) ---
                    try:
                        import platform, subprocess
                        system = platform.system()
                        title = "👻 Vibrisse Ghost"
                        clean_msg = f"Modification terminée dans {os.path.basename(file_path)}".replace('"', "'")
                        
                        if system == 'Darwin': # macOS
                            script = f'display notification "{clean_msg}" with title "{title}" sound name "Glass"'
                            subprocess.run(['osascript', '-e', script])
                        elif system == 'Linux': # Linux
                            subprocess.run(['notify-send', title, clean_msg, '-i', 'utilities-terminal'])
                        elif system == 'Windows': # Windows
                            ps_script = f'[void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms"); $objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon; $objNotifyIcon.Icon = [System.Drawing.SystemIcons]::Information; $objNotifyIcon.BalloonTipIcon = "Info"; $objNotifyIcon.BalloonTipText = "{clean_msg}"; $objNotifyIcon.BalloonTipTitle = "{title}"; $objNotifyIcon.Visible = $True; $objNotifyIcon.ShowBalloonTip(10000);'
                            subprocess.run(['powershell', '-Command', ps_script])
                    except: pass

                    print(f"--- 👻 GHOST NOTIF : Enregistrée et notifiée ---", flush=True)
                except Exception as ne:
                    print(f"--- ❌ GHOST NOTIF ERROR : {ne} ---", flush=True)
                    logger.error(f"Error saving ghost notification: {ne}")
            else:
                print(f"--- ⚠️ GHOST FAILED : Réponse LLM invalide ou vide ---", flush=True)
                
        except Exception as e:
            logger.error(f"Erreur exécution Ghost Task: {e}")

    @staticmethod
    def is_ghost_locked(file_path: str) -> bool:
        return file_path in GhostService.processing_files

