# scripts/ingest.py
import asyncio
from app.services.vector_service import VectorService
from app.ingestion.processor import IngestionProcessor

async def main():
    vs = VectorService()
    processor = IngestionProcessor(vs)
    
    # On indexe le code à analyser ET le code de l'application elle-même
    targets = ["./data/source_code", "./app", "./scripts"]
    
    print("🧠 Initialisation du moteur vectoriel...")
    for target in targets:
        print(f"Indexation de : {target}")
        await processor.run_ingestion(target)
    
    print("✨ C'est prêt ! Tout est indexé.")

if __name__ == "__main__":
    asyncio.run(main())