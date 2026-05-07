import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any

class ThreadService:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent.parent.parent / "data" / "checkpoints.db"

    def list_threads(self) -> List[Dict[str, Any]]:
        """Liste tous les threads disponibles dans la base de checkpoints."""
        if not self.db_path.exists():
            return []
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Dans LangGraph AsyncSqliteSaver, les threads sont dans la table 'checkpoints'
            # On cherche les thread_id uniques
            cursor.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id DESC")
            threads = cursor.fetchall()
            
            result = []
            for (tid,) in threads:
                # On tente de récupérer le dernier message pour donner un titre
                # C'est un peu complexe car le contenu est sérialisé en binaire/pickled par LangGraph
                # Pour l'instant, on renvoie juste l'ID et un titre placeholder
                result.append({
                    "id": tid,
                    "title": f"Session {tid[:8]}",
                    "updated_at": "N/A" # On pourrait extraire le timestamp si besoin
                })
            
            conn.close()
            return result
        except Exception as e:
            print(f"⚠️ ThreadService Error: {e}")
            return []

    def delete_thread(self, thread_id: str) -> bool:
        """Supprime un thread et tous ses checkpoints."""
        if not self.db_path.exists():
            return False
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
            cursor.execute("DELETE FROM writes WHERE thread_id = ?", (thread_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"⚠️ ThreadService Delete Error: {e}")
            return False

thread_service = ThreadService()
