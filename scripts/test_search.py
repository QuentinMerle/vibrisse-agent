# scripts/test_search.py
import asyncio
import sys
import os

# On ajoute le répertoire racine au path pour que Python trouve 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vector_service import VectorService

async def run_test():
    # Initialisation du service (Lancement d'Ollama requis en fond)
    vs = VectorService()
    retriever = vs.get_retriever()
    
    # Ta requête orientée Next.js / Sanity
    query = "Montre-moi comment les types TypeScript sont définis pour les documents Sanity"
    
    print(f"\n🔍 RECHERCHE : {query}")
    print("="*50)
    
    # Déclenchement de la recherche hybride/parent
    docs = retriever.get_relevant_documents(query)
    
    if not docs:
        print("❌ Aucun résultat trouvé. As-tu bien lancé l'ingestion avant ?")
        return

    for i, doc in enumerate(docs):
        source = doc.metadata.get('source', 'Inconnue')
        print(f"\n[RÉSULTAT {i+1}] Source: {source}")
        print("-" * 20)
        # On affiche un bloc significatif pour vérifier le "Parent Document"
        print(doc.page_content[:600] + "...") 
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(run_test())