from app.services.rag.vector_service import VectorService

# Instance unique partagée par tout l'app (API, Nodes, Watchdog)
vs = VectorService()
