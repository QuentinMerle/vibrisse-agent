# app/services/context_service.py
import re

class ContextService:
    @staticmethod
    def compress_code(code: str, relevant_text: str = "", threshold: int = 50) -> str:
        """
        Implémente la technique du 'Skeletal Context'.
        Garde le bloc pertinent intact, mais réduit le reste du fichier à ses signatures.
        """
        lines = code.splitlines()
        
        # Si le fichier est petit, pas besoin de s'embêter
        if len(lines) <= threshold:
            return code

        # 1. Identifier les lignes "cibles" (celles qui matchent la recherche)
        # On utilise une recherche floue simple pour trouver l'index de début/fin
        target_indices = []
        if relevant_text:
            # On cherche les 3 premières lignes du relevant_text pour plus de fiabilité
            search_anchor = "\n".join(relevant_text.splitlines()[:3])
            if search_anchor in code:
                start_index = code.find(search_anchor)
                start_line = code.count("\n", 0, start_index)
                end_line = start_line + relevant_text.count("\n") + 2
                target_indices = list(range(max(0, start_line - 2), min(len(lines), end_line + 5)))

        # 2. Algorithme de compression universel
        # Patterns de signatures courants (Python, JS, TS, Go, etc.)
        signature_patterns = [
            r"^\s*(class|def|function|async|export|interface|type|enum|struct|trait)\b",
            r"^\s*[a-zA-Z0-9_]+\s*\([^)]*\)\s*[:{]", # Fonctions C-style ou Python sans mot clé
            r"^\S" # Toute ligne commençant à l'indentation 0 (souvent important)
        ]
        
        compressed_lines = []
        is_hiding = False
        
        for i, line in enumerate(lines):
            # Si c'est une ligne cible, on la garde intacte
            if i in target_indices:
                if is_hiding:
                    compressed_lines.append("    # ... [implémentation masquée pour économiser du contexte] ...")
                    is_hiding = False
                compressed_lines.append(line)
                continue
            
            # Vérifier si la ligne est une signature ou une structure importante
            is_signature = any(re.search(p, line) for p in signature_patterns)
            
            if is_signature:
                if is_hiding:
                    compressed_lines.append("    # ... [implémentation masquée] ...")
                    is_hiding = False
                compressed_lines.append(line)
            else:
                # C'est du corps de fonction/classe non pertinent
                is_hiding = True
                
        if is_hiding:
            compressed_lines.append("    # ... [implémentation masquée] ...")

        return "\n".join(compressed_lines)

context_service = ContextService()
