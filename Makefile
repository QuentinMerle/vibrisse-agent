# Variables
PYTHON = .venv/bin/python
PIP = .venv/bin/pip
UVICORN = .venv/bin/uvicorn

.PHONY: install dev health pull-models

# Equivalent de 'npm install'
install:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Equivalent de 'npm run dev'
dev:
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

# Vérifier si Ollama et le modèle sont prêts
health:
	curl http://localhost:11434/api/tags
	@echo "\n---"
	@curl -I http://localhost:8000/health

# Pull les modèles nécessaires
pull-models:
	ollama pull gemma4:e4b
	ollama pull nomic-embed-text

# Alias pour l'ingestion
ingest:
	@echo "🚀 Synchronisation du code..."
	@python scripts/ingest.py

# Alias pour tester la recherche
search:
	@python scripts/test_search.python

# Alias pour tester les guardrails
stresstest:
	@python scripts/stress_test_guardrails.py

# Évaluation de la qualité (RAGAS / DeepEval)
evaluate:
	@echo "Lancement de l'évaluation avec un modèle juge..."
	# Ici on peut spécifier un modèle différent pour le juge
	OLLAMA_MODEL=llama3 python3 scripts/evaluate_rag.py

# Évaluation de la fiabilité
reliability:
	@python scripts/run_reliability_suite.py

stats:
	@echo "📊 Poids du projet Vibrisse Agent :"
	@du -sh ./data 2>/dev/null || echo "Pas encore de données."
	@echo "\n🔍 Détails :"
	@du -sh ./data/chroma_db 2>/dev/null || echo "ChromaDB: Non créé"
	@du -sh ./data/parent_documents 2>/dev/null || echo "Docs: Non créés"
	@if [ -f ./data/hashes.json ]; then du -sh ./data/hashes.json; else echo "Hashes: Non générés"; fi

clean-db:
	rm -rf chroma_db/