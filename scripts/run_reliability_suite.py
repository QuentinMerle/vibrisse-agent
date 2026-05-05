import json
from app.services.llm_service import LLMService
from app.services.vector_service import VectorService
from app.core.factory import LLMFactory
from ragas import evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy
from ragas.run_config import RunConfig
from datasets import Dataset

def run_suite():
    # 1. Charger le dataset de référence
    with open("data/eval_dataset.json", "r") as f:
        eval_data = json.load(f)

    llm_service = LLMService()
    vector_service = VectorService()
    
    results = []

    print(f"🚀 Évaluation de {len(eval_data)} questions en cours...")

    for item in eval_data:
        query = item["question"]
        
        # Récupération (Context)
        docs = vector_service.search(query)
        context = [d.page_content for d in docs]
        
        # Génération (Answer)
        response = llm_service.generate_guarded_answer(query, docs)
        
        results.append({
            "question": query,
            "answer": response.answer,
            "contexts": context,
            "ground_truth": item["ground_truth"]
        })

    # 2. Transformer pour RAGAS
    dataset = Dataset.from_list(results)
    
    # 3. Évaluation (Le Juge)
    juge = LLMFactory.get_model(purpose="evaluation")
    # 1. On récupère les embeddings configurés (LOCAUX par défaut)
    embeddings = LLMFactory.get_embeddings()
    
    # On initialise les métriques avec le juge
    metrics = [
        Faithfulness(llm=juge),
        AnswerRelevancy(llm=juge)
    ]
    
    # Configuration pour éviter les Timeouts sur Mac Local
    run_config = RunConfig(
        timeout=600, # 10 minutes
        max_workers=2 # Seulement 2 tâches en parallèle pour ne pas saturer Ollama
    )
    
    score = evaluate(
        dataset, 
        metrics=metrics, 
        llm=juge, 
        embeddings=embeddings,
        run_config=run_config
    )
    
    print("\n--- 📊 SCORE FINAL ---")
    print(score)

if __name__ == "__main__":
    run_suite()