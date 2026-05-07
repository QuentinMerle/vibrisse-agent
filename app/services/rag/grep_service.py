import subprocess
import os
import re
from typing import List, Dict
from pathlib import Path
from langchain_core.documents import Document

class GrepService:
    def __init__(self, target_path: str):
        self.target_path = target_path

    def extract_technical_terms(self, query: str) -> List[str]:
        """Extrait les termes techniques potentiels d'une requête (SnakeCase, camelCase, etc.)."""
        # On cherche les mots qui ressemblent à du code
        pattern = r'[a-zA-Z_][a-zA-Z0-9_]*'
        words = re.findall(pattern, query)
        
        # On filtre les mots trop courts ou trop communs (simple heuristique)
        common_words = {"the", "and", "how", "what", "where", "this", "that", "code", "file", "project"}
        technical_terms = [w for w in words if len(w) > 3 and w.lower() not in common_words]
        
        return list(set(technical_terms))

    def fast_search(self, query: str, limit: int = 3) -> List[Document]:
        """Exécute ripgrep pour trouver des correspondances exactes."""
        terms = self.extract_technical_terms(query)
        if not terms:
            return []

        # On prend les 3 termes les plus "uniques" (les plus longs pour l'instant)
        terms = sorted(terms, key=len, reverse=True)[:3]
        
        results = []
        seen_files = set()
        
        for term in terms:
            if len(results) >= limit:
                break
                
            try:
                # Commande rg : -l pour lister les fichiers, --max-count pour limiter par fichier
                # On ignore explicitement les dossiers de build et dépendances
                cmd = [
                    "rg", "-l", "--max-count", "1", 
                    "-g", "!node_modules/*", 
                    "-g", "!.next/*", 
                    "-g", "!dist/*", 
                    "-g", "!build/*", 
                    "-g", "!.git/*",
                    term, self.target_path
                ]
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                
                if process.returncode == 0:
                    files = process.stdout.strip().split('\n')
                    for f_path in files:
                        if f_path and f_path not in seen_files:
                            if len(results) >= limit:
                                break
                                
                            # On charge le contenu du fichier
                            try:
                                with open(f_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    results.append(Document(
                                        page_content=content,
                                        metadata={
                                            "source": f_path,
                                            "method": "surgical_grep",
                                            "matched_term": term
                                        }
                                    ))
                                    seen_files.add(f_path)
                            except:
                                continue
            except subprocess.TimeoutExpired:
                continue
            except Exception as e:
                print(f"⚠️ Grep error: {e}")
                continue
                
        return results
