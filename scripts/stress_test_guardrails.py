import sys
from pathlib import Path

# Ajout du dossier app au path pour l'import
sys.path.append(str(Path(__file__).parent.parent))

from app.services.llm_service import LLMService
from pydantic import ValidationError

def run_stress_test():
    llm = LLMService()
    
    # 1. On simule un contexte restreint (ce que ton VectorService renverrait)
    fake_context = [
        type('obj', (object,), {
            "metadata": {"file_path": "src/auth.ts", "function_name": "login"}
        }),
        type('obj', (object,), {
            "metadata": {"file_path": "src/api.ts", "function_name": "fetchData"}
        })
    ]

    # 2. LA QUESTION PIÈGE
    # On force le LLM à parler d'une fonction 'deleteEverything()' qui n'est pas dans le contexte
    prompt_piege = "Explique-moi comment fonctionne la fonction deleteEverything() dans le fichier database.ts"

    print("--- 🚀 LANCEMENT DU STRESS TEST ---")
    print(f"Question : {prompt_piege}")
    print(f"Contexte autorisé : {[d.metadata['file_path'] for d in fake_context]}")
    print("-" * 35)

    try:
        # On tente de générer la réponse
        response = llm.generate_guarded_answer(prompt_piege, fake_context)
        
        print("❌ ÉCHEC DU TEST : Le LLM a réussi à passer à travers les mailles du filet !")
        print(f"Réponse frauduleuse : {response.json()}")
        
    except Exception as e:
        print("✅ SUCCÈS DU TEST : Le Guardrail a bloqué l'hallucination.")
        print(f"Erreur capturée : {e}")

if __name__ == "__main__":
    run_stress_test()