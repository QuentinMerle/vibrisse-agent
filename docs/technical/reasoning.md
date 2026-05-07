# Système de Raisonnement & Agents

## 🎭 Supervisor / Worker
Vibrisse n'est pas un agent monolithique mais une équipe d'experts :
- **Supervisor (Router)** : Analyse l'intention et délègue au bon worker.
- **Workers** :
    - `coder` : Expert en écriture et refactoring.
    - `writer` : Expert en documentation et vulgarisation.
    - `architect` : Analyse de haut niveau et design patterns.

## 🧠 Skills (Compétences)
Les instructions sont isolées dans `app/agents/skills/*.md`. Cela permet de modifier le comportement de l'IA sans toucher au code Python.

## 🛡️ Robustesse (Parsers)
Les nœuds de décision implémentent un parsing multi-couches :
1. Tentative de lecture du **JSON**.
2. Fallback sur les balises **XML** (`<datasource>`, `<worker>`).
3. Fallback sur l'extraction de **Mots-clés**.

## 🔄 Persistence & Streaming
- **SSE Protocol** : Communication temps-réel avec le client.
- **SQLite Persistence** : Les conversations sont stockées de manière permanente dans `checkpoints.db`.
- **History Merging** : Fusion des messages consécutifs de l'agent pour une interface propre.
