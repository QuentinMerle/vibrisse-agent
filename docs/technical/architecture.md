# Architecture Détillée - Vibrisse Agent

## 🏗️ Structure Backend (`app/`)
Le backend suit une structure Domain-Driven Design (DDD) légère :
- `app/agents/`: Logique agentique.
    - `graph.py`: Définition du graphe d'états LangGraph.
    - `nodes/`: Nœuds isolés (`vision`, `retrieval`, `generation`, `tool_execution`).
- `app/services/`: Couche logique métier.
    - `llm/`: Factory et services liés aux modèles.
    - `rag/`: Gestion de l'indexation et du stockage vectoriel.
    - `mcp/`: Client pour la connexion aux serveurs d'outils externes.
    - `core/`: Services transversaux (SSE, onboarding, watchers, evaluation, sovereign_routing).
- `app/api/`: Points d'entrée FastAPI.

## 🌊 Flux Global (LangGraph)
```mermaid
graph TD
    User((User)) --> Router{🧠 Router}
    Router -->|Planning Needed| Planning[🏛️ Planning Node]
    Planning -->|Approval| Coder
    Router -->|Technical Task| Coder[👷 Coder Worker]
    Router -->|RAG Needed| RAG[Surgical Retrieval]
    RAG --> Coder
    Coder --> Tools[🛠️ Tool Execution]
    Tools --> Coder
    Coder --> Result((Response))
```

## ⚖️ Sovereign Routing (Smart Offloading)
```mermaid
sequenceDiagram
    participant U as User
    participant S as Sovereign Sentinel
    participant C as Cloud LLM
    participant L as Local Ollama

    U->>S: Requête technique (ex: "list files")
    S->>S: Analyse complexité
    alt Task Simple
        S-->>U: Proposition: "Détourner vers Local ?"
        U->>L: Confirmation
        L-->>U: Réponse locale (0 tokens cloud)
    else Task Complexe
        S->>C: Exécution Cloud (Précision max)
        C-->>U: Réponse
    end
```

## 🎨 Frontend (`frontend/`)
- **Tech Stack** : React + Vite + Vanilla CSS.
- **Esthétique** : "Obsidian Glass" (transparences, flous, contrastes élevés).
- **Composants Clés** :
    - `VibrisseAvatar` : Réagit aux états de réflexion.
    - `ThinkingConsole` : Affiche le flux de pensée de l'agent.
