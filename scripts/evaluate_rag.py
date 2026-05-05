import os
import sys
from pathlib import Path

# Ajout du dossier racine au sys.path pour l'import de 'app'
sys.path.append(str(Path(__file__).parent.parent))

from app.core.factory import LLMFactory
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from datasets import Dataset

# Initialisation dynamique via la Factory
juge_llm = LLMFactory.get_model(purpose="evaluation")
embeddings_model = LLMFactory.get_embeddings()

def run_evaluation(results_list):
    """
    results_list doit être une liste de dicts:
    {"question": "...", "answer": "...", "contexts": ["...", "..."]}
    """
    if not results_list:
        print("⚠️ Liste de résultats vide.")
        return None

    dataset = Dataset.from_list(results_list)
    
    # On utilise les modèles de la Factory
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy],
        llm=juge_llm,
        embeddings=embeddings_model
    )
    
    print("\n--- 🏆 RÉSULTATS DE L'ÉVALUATION ---")
    print(result)
    return result

if __name__ == "__main__":
    print("🚀 Test à blanc (Gemini Judge)...")
    sample_data = [
        {
            "question": "Comment fonctionne le système de guardrails ?",
            "answer": "Le système utilise Instructor pour valider les schémas Pydantic.",
            "contexts": ["Instructor wrappe le client LLM pour appliquer des validateurs Pydantic."]
        }
    ]
    run_evaluation(sample_data)