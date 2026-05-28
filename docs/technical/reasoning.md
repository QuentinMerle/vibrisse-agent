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

## 🏛️ Planning Mode (Human-in-the-Loop)
Vibrisse Agent intègre un mode de planification pour les tâches complexes, permettant à l'utilisateur de valider l'approche avant l'exécution :
- **`planning_node`** : Génère un plan détaillé enveloppé dans des balises `<artifact>`.
- **Interruption** : Utilise la fonctionnalité `interrupt_after` de LangGraph pour mettre l'exécution en pause.
- **Frontend Approval** : L'UI affiche une demande d'approbation et reprend l'exécution dynamiquement (`resume`).
