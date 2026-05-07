# Moteur de Recherche Hybride (RAG)

Vibrisse utilise une approche à trois couches pour garantir une précision chirurgicale sur le code source.

## 🔍 Les trois couches
1. **Surgical Grep (Fast-Track)** : 
   Utilise `ripgrep` pour trouver des correspondances exactes sur des termes techniques (noms de fonctions, variables). C'est la couche la plus rapide et la plus fiable pour le code.
2. **Dense (ChromaDB)** : 
   Recherche sémantique vectorielle pour comprendre le contexte et les concepts ("Comment fonctionne l'auth ?").
3. **Sparse (BM25)** : 
   Recherche par fréquence de termes pour équilibrer la sémantique et les mots-clés.

## 🛡️ Safety Ingestion Shield
Pour protéger les ressources système :
- **Batch Processing** : Indexation par paquets de 50 fichiers.
- **Size Filtering** : Fichiers > 1MB ignorés.
- **Intelligent Exclusions** : `node_modules`, `.git`, `dist`, `build`, etc., sont exclus par défaut.

## ✂️ Context Pruning
Avant l'envoi au LLM, le contexte est "nettoyé" :
- Suppression des headers de licence.
- Suppression des blocs de commentaires massifs non pertinents.
- Réduction des espaces blancs.
- Résultat : ~20% d'économie de tokens.
