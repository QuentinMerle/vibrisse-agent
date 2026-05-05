# Vibrisse Agent - Context & Guidelines

Ce fichier sert de mémoire technique pour les agents IA travaillant sur ce projet. Il définit l'architecture, les standards et l'état actuel du système.

## 🚀 Vue d'ensemble Technique
**Vibrisse Agent** est un assistant IA agentique conçu par **Vibrisse Studio** pour l'ingénierie **Vibrisse AI**. Il permet d'interagir avec des bases de code locales via une architecture de graphe (LangGraph) et une interface moderne (React).

### Stack Technologique
- **Backend** : FastAPI (Python 3.11+)
- **Agentic Logic** : LangGraph (LangChain ecosystem)
- **Frontend** : React + Vite + Vanilla CSS (Obsidian Glass Aesthetic)
- **Vector DB** : ChromaDB (pour le RAG)
- **Protocole** : MCP (Model Context Protocol) pour l'extensibilité des outils.

### Interfaces
- **Web UI** : React + Vite (Mode Studio Cockpit).
- **TUI (Terminal)** : Python Rich + Prompt Toolkit (Mode Hacker).
- **CLI** : Script unifié `vibrisse-cli.sh` pour la gestion des modes.

---

## 🏗️ Architecture (Post-Refactoring)

### Backend (`app/`)
Le backend suit une structure par domaine (Domain-Driven Design léger) :
- `app/agents/` : Logique agentique.
    - `graph.py` : Définition du graphe d'état.
    - `nodes/` : Chaque nœud du graphe est isolé (`vision`, `retrieval`, `generation`, `tool_execution`).
- `app/services/` : Couche logique métier.
    - `llm/` : Factory et services liés aux modèles.
    - `rag/` : Gestion de l'indexation et du stockage vectoriel (ChromaDB + BM25).
    - `mcp/` : Client pour connecter des serveurs d'outils externes.
    - `core/` : Services transverses (SSE streaming, onboarding manifest, watchers, evaluation/Ragas).
- `app/schemas/` : Définitions Pydantic centralisées.

### 🧠 Logiciel de Raisonnement (Cerveau)

1. **Génération de Manifeste (Onboarding)** :
    Au démarrage, `onboarding_service` scanne `TARGET_PROJECT_PATH` pour identifier la stack (Docker, Python, Node, etc.). Ce manifeste est injecté dans le système prompt pour donner à l'agent une "conscience" immédiate du projet.
2. **Hybrid Retrieval Architecture** :
    Vibrisse combine deux moteurs via `rank_bm25` :
    - **Dense (ChromaDB)** : Pour le sens sémantique et conceptuel.
    - **Sparse (BM25)** : Pour les correspondances de termes exacts (ex: noms de fonctions, IDs).
3. **SSE Streaming Protocol** :
    Toute communication agent -> client passe par `StreamService`. Les événements sont typés : `token` (texte), `thought` (raisonnement), `status` (badges UI), `metadata` (contexte).

### 🧠 Système de Raisonnement & Prompts

Vibrisse utilise une approche hybride pour ses instructions :

1. **Modular Skills (`app/agents/skills/`)** : 
   Les expertises métier sont stockées dans des fichiers Markdown indépendants. 
   - `code_expert.md` : Instructions pour l'analyse et la génération de code.
   - `tool_expert.md` : Guide d'utilisation des outils (Web, Terminal).
   - `orchestrator.md` : Logique de planification et de synthèse.
   - *Avantage* : On peut modifier le "savoir" de l'agent sans toucher au code Python. Chargé via `utils.load_skill()`.

2. **System Prompts (In-Node)** :
   Les instructions structurelles (format de sortie, gestion des pensées) sont définies directement dans les nœuds (`router.py`, `generation.py`). 
   - Elles utilisent les balises `<thought>` pour extraire le raisonnement avant la réponse finale.
   - Elles sont optimisées pour le streaming token par token.

3. **Le Routeur : L'Aiguilleur du Ciel** :
   Le nœud `router.py` analyse l'intention et choisit entre 3 chemins :
   - `vectorstore` : Déclenche le RAG sur le code local.
   - `web_and_tools` : Déclenche l'agent autonome capable d'utiliser Google, le Terminal ou les outils MCP.
   - `direct_response` : Pour les salutations ou les connaissances générales ne nécessitant pas de preuves.

### 📊 Observabilité Technique (Evals)

Vibrisse implémente un pipeline d'évaluation **100% Local** via Ragas :
1. **LocalJSONJudge Pattern** : Pour pallier la loquacité des modèles locaux (`llama3:8b`), le juge est encapsulé dans une classe héritant de `BaseChatModel`. Elle intercepte les sorties, extrait le JSON par Regex et garantit un format compatible avec Ragas.
2. **Dynamic Model Injection** : Les modèles de juge et d'embeddings sont injectés dynamiquement depuis le `.env` au moment de l'évaluation pour éviter les conflits de configuration globale.
3. **Hardware Requirement** : L'évaluation nécessite impérativement un modèle 8B+ (`RAGAS_MODEL`) pour garantir la fiabilité des scores de fidélité.

### Frontend (`frontend/src/`)
Architecture modulaire et orientée hooks :
- `components/` : Composants UI atomiques (Chat, Layout, Settings).
- `hooks/` : Logique d'état déportée (`useChat`, `useConfig`).
- `services/api.js` : Client API centralisé (Port 8001).

---

## ⚠️ Points de Vigilance Critiques

### 🎯 Calibrage du Routeur (`app/agents/nodes/router.py`)

Le **routeur** est le composant le plus fragile et le plus important du système. Il prend la décision initiale qui oriente toute la chaîne de raisonnement (`vectorstore` → RAG, `web_and_tools` → Outils, `direct_response` → Réponse directe).

**Ce qui a été appris :**
- Le routeur demande un **calibrage long et itératif** par prompting. Une formulation imprécise envoie la requête dans le mauvais nœud, et l'IA échoue *en silence* (ex: question météo routée vers RAG → aucun résultat → réponse vide).
- **Les modèles locaux** (Ollama) sont particulièrement sensibles : un prompt trop long ou mal structuré provoque une sortie JSON invalide que le parser Pydantic rejette.
- **Stratégie de test recommandée** : Avant de changer le prompt du routeur, tester explicitement au moins 3 cas par catégorie :
  - `vectorstore` : questions sur le code local (ex: *"Comment fonctionne X dans ce projet ?"*)
  - `web_and_tools` : questions temps réel (ex: *"Quelle est la météo à Y ?"*)
  - `direct_response` : connaissances générales (ex: *"Explique-moi le pattern Observer"*)
- **Ne jamais modifier le routeur et un autre nœud dans le même commit.** En cas de régression, il est impossible de savoir quel composant est responsable.

### 🚧 Avertissement : Montées de Version LangChain/LangGraph

> **⚠️ RISQUE ÉLEVÉ** : Mettre à jour `langchain-core`, `langgraph`, `langchain-community` ou `langchain-tavily` peut provoquer des **régressions silencieuses** sans erreur explicite.

**Régressions documentées lors des montées de version :**

| Package | Changement | Impact observé |
| :--- | :--- | :--- |
| `langchain-tavily` ≥ 0.1.0 | `search.invoke()` retourne une `str` au lieu d'une `List[dict]` | Erreur `'str' object has no attribute 'get'` |
| `langchain-core` ≥ 0.2 | Les objets messages n'ont plus d'attribut `.role` | Erreur `'HumanMessage' has no attribute 'role'` — utiliser `.type` |
| `langgraph` ≥ 0.2 | Les nœuds doivent être des `async generator` pour le streaming | Les nœuds en `return` bloquent le stream SSE et les pensées |
| `langchain-community` | `DuckDuckGoSearchRun` dépend de `ddgs` non-installé par défaut | `ImportError: Could not import ddgs` |

**Procédure de montée de version recommandée :**
1. Créer une branche dédiée.
2. Mettre à jour **un seul package** à la fois.
3. Tester les 3 routes du routeur (voir ci-dessus).
4. Vérifier la `ThinkingConsole` (les pensées doivent s'afficher à chaque étape).
5. Vérifier que les outils (`web_search`, `run_terminal_command`) retournent des strings propres.
6. Merger seulement si tout est vert.

---

## 🛠️ Standards de Développement

1. **Modularité** : Pas de "God Objects". Fichiers < 300 lignes privilégiés.
2. **Streaming** : Réponses via SSE obligatoires.
3. **Reasoning** : Inclusion systématique des balises `<thought>`.
4. **UI Aesthetics** : Design "Obsidian Glass" (Violet/Indigo). **Lire `DESIGN.md` avant tout travail UI.** Ne jamais inventer un token de couleur ou une police.
5. **Error Handling** : Utilisez des exceptions Pydantic pour la validation et renvoyez des messages clairs via le stream `status` en cas d'échec d'outil.
6. **Graceful Shutdown** : Le launcher `vibrisse-cli.sh` gère les groupes de processus pour assurer une fermeture propre des workers Ragas et éviter les fuites de sémaphores.

---

## 📋 État Actuel & Roadmap
- [x] **Structure** : Refactoring Backend et Frontend terminés.
- [x] **UX/UI Studio** : Sidebar Slim, Shortcuts, Welcome Screen et Skeletons implémentés.
- [x] **Interfaces** : Web UI et TUI (Terminal) fonctionnelles.
- [ ] **Industrialisation** : Packaging (Docker/Electron) et documentation publique.
- [ ] **Sécurité** : Finalisation de l'audit des outils MCP.
- [ ] **Multi-Agent Architecture** : Passage à une orchestration de sous-agents spécialisés.
- [x] **Framework d'Évaluation (Evals)** : Mesure de précision RAG (Ragas/LangSmith) intégrée.
- [ ] **Optimisation Contextuelle** : Compression de prompt et quantization pour LLMs locaux.
- [ ] **Internationalisation (i18n)** : Passage des prompts système et des skills en anglais pour une meilleure compatibilité LLM.

## 🔑 Commandes Utiles
- **Lancer Vibrisse (Web)** : `./vibrisse-cli.sh`
- **Lancer Vibrisse (TUI)** : `./vibrisse-cli.sh --tui` (ou `vibrisse-tui`)
- **Démarrer en Dev (Front)** : `cd frontend && npm run dev`
- **Build Production** : `cd frontend && npm run build`
