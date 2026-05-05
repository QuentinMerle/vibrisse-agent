# 🐱 Vibrisse Agent : L'assistant IA qui comprend ton code 🚀

[![English](https://img.shields.io/badge/lang-English-blue)](file:///README.md)
[![Français](https://img.shields.io/badge/lang-Français-red)](#)
[![Vibrisse - Studio Grade UI](https://img.shields.io/badge/UI-Studio--Grade-7b39ed)](file:///AGENTS.md)
[![Local First](https://img.shields.io/badge/Local--First-Ollama-10b981)](https://ollama.com)
[![MCP Powered](https://img.shields.io/badge/MCP-Extensible-yellow)](https://modelcontextprotocol.io)

**Vibrisse Agent** est un assistant IA agentique "Studio-Grade" conçu par **Vibrisse Studio**. Aboutissement de la curiosité d'un développeur originaire du Web, cet outil transforme tes bases de code locales en partenaires de conversation intelligents. Construit sur une architecture **LangGraph** et optimisé pour le **100% local**, il incarne l'expertise de notre service **Vibrisse AI**.

<p align="center">
  <img src="./docs/assets/vibrisse-agent-ui.png" alt="Vibrisse Studio UI" width="100%">
</p>

---

## ✨ Points Forts (The Studio Experience)

### 📊 Observabilité & Évaluation (Ragas)
Vibrisse intègre le framework **RAGAS** pour évaluer la fidélité (anti-hallucination) et la pertinence des réponses en temps réel.

### 🎨 Double Interface de Contrôle
*   **Studio Web UI (Cockpit)** : Une interface "Obsidian Glass" immersive avec sidebar intelligente, monitoring du contexte en temps réel et rendu Markdown haute définition.
*   **Hacker TUI (Terminal)** : Une interface textuelle ultra-rapide en violet indigo pour piloter l'agent sans quitter ton terminal.
*   **Fluidité Totale** : Raccourcis clavier (`CMD+K`, `CMD+B`), skeleton loading et animations de précision.

### 🧠 Intelligence Contextuelle
*   **RAG Hybride** : Recherche vectorielle (sens) couplée à une recherche BM25 (mots-clés) pour une précision chirurgicale sur le code.
*   **Project Onboarding** : Scan automatique de l'architecture, lecture des manifestes (`README.md`, `CONTEXT.md`) pour une prise de conscience immédiate du projet.
*   **Modular Skills** : Instructions d'expertise isolées dans des fichiers Markdown (`app/agents/skills/`), permettant de modifier le comportement de l'agent sans changer une seule ligne de code.

### 🔌 Extensibilité (MCP)
*   **Model Context Protocol** : Vibrisse est nativement compatible avec les serveurs MCP. Connecte ton agent à GitHub, Linear, Slack ou tes propres outils personnalisés en quelques secondes.
*   **Tool Execution Control** : Tu gardes le contrôle total avec une validation explicite (HITL) avant chaque exécution de commande système.

---

## 🚀 Démarrage Rapide

### Pré-requis
*   [Ollama](https://ollama.com/) installé et lancé.
*   Python 3.11+
*   Node.js & npm (pour le frontend)

### Installation & Lancement
```bash
# Cloner le projet
git clone https://github.com/QuentinMerle/vibrisse-agent.git
cd vibrisse-agent

# Lancement automatique (Onboarding & Install)
./vibrisse-cli.sh --onboard

# Lancer en mode Studio (Web UI)
./vibrisse-cli.sh

# Lancer en mode Hacker (Terminal TUI)
./vibrisse-cli.sh --tui
```

---

## ⚙️ Configuration (Variables d'Environnement)

Vibrisse se configure via un fichier `.env`. Voici les variables clés :

| Variable | Défaut | Description |
| :--- | :--- | :--- |
| `TARGET_PROJECT_PATH` | `.` | Chemin du dossier de code à analyser |
| `LLM_PROVIDER` | `ollama` | `ollama` (local), `ollama_cloud`, `groq` ou `openrouter` |
| `LLM_MODEL` | `gemma4:e2b` | Modèle principal pour le chat |
| `ENABLE_WEB_SEARCH` | `true` | Autorise l'agent à chercher sur le web (Tavily/DDG) |
| `TAVILY_API_KEY` | - | Clé API pour la recherche web (optionnel, fallback DDG) |
| `RAGAS_MODEL` | `llama3:8b` | Modèle utilisé pour le juge d'évaluation (8B+ recommandé) |

---

## ⌨️ Raccourcis Productivité

| Touche | Action |
| :--- | :--- |
| `CMD + K` | Focus instantané sur la barre de saisie |
| `CMD + B` | Réduire / Agrandir la sidebar (Mode Slim) |
| `CMD + N` | Lancer une nouvelle discussion propre |
| `/ui` (TUI) | Basculer du terminal vers l'interface Web |

---

## 🛡️ Sécurité & Confidentialité

Vibrisse est conçu avec une approche **Security-by-Design** pour protéger ton code et tes données.

*   **Local-First & Souveraineté** : Si tu utilises Ollama, aucune ligne de ton code ou de tes conversations ne quitte ta machine. Vibrisse fonctionne parfaitement en mode déconnecté.
*   **Contrôle Total (Human-in-the-Loop)** : L'agent a l'interdiction d'exécuter des commandes système (`run_terminal_command`) sans une validation explicite de ta part dans l'interface.
*   **Masquage des Secrets (Scrubbing)** : Un système de filtrage automatique masque les clés API, tokens et mots de passe qui pourraient apparaître accidentellement dans les logs de l'agent.
*   **Isolation des Données** : Ton historique de chat et tes index vectoriels sont stockés localement dans le dossier `/data`, lequel est strictement exclu de tout tracking Git.

---

## 🏗️ Architecture & 📂 Arborescence

Vibrisse suit une architecture modulaire pour séparer l'intelligence (LLM) de l'infrastructure (API/UI).

```text
.
├── app/                # Backend FastAPI & Logique Agentique (LangGraph)
├── data/               # Index vectoriels & Base de données locale
├── docs/               # Documentation détaillée (Business, Tech, Roadmap)
├── frontend/           # Interface React Studio (Vite + Vanilla CSS)
├── AGENTS.md           # Instructions & Mémoire technique pour les IA
├── DESIGN.md           # Design System "Obsidian Glass" (Source de vérité UI)
├── README.md           # Cette documentation
└── vibrisse-cli.sh     # Launcher unifié (Backend + Frontend)
```

---

## 🚨 Pièges & Gotchas

### Le Routeur : cœur fragile du système
Le **routeur** (`app/agents/nodes/router.py`) est le composant critique qui décide comment traiter chaque message. Son calibrage est un travail **long et itératif**. Se référer au tableau de tests dans `AGENTS.md` avant toute modification.

### ⚠️ Monter de version LangChain ?
Le projet utilise des fonctionnalités de pointe de LangGraph et LangChain. Les montées de version peuvent introduire des **breaking changes silencieux** (ex: changement de format de retour des outils). Mettre à jour un seul package à la fois et tester rigoureusement.

---

## 🤖🤝🧠 L'Esprit Vibrisse : L'Alliance IA-Humain

Vibrisse n'est pas qu'un outil, c'est une étude sur la collaboration. Nous croyons que l'IA excelle dans l'algorithmique et le parsing, tandis que l'humain apporte l'intuition systémique. 

> *Note de dév : Vibrisse a été conçu par une IA et un humain travaillant en binôme serré. Cette synergie est au cœur de chaque ligne de code.*

---

## ⚖️ Clause de non-responsabilité

Vibrisse Agent est un outil expérimental utilisant des modèles de langage (LLM) pour générer et exécuter du code. Bien qu'il intègre des mécanismes de sécurité (HITL), l'utilisateur reste seul responsable des commandes validées et des modifications apportées à son système. Vibrisse Studio ne pourra être tenu responsable d'aucune perte de données ou dommage causé par l'utilisation de cet assistant.

---

## 📚 Sources & Inspiration
*   [IBM Technology](https://www.youtube.com/@IBMTechnology) — Pour les concepts fondamentaux d'architecture IA.
*   [Google Cloud: What is Prompt Engineering?](https://cloud.google.com/discover/what-is-prompt-engineering) — Principes de base du prompting.
*   [Gemini API: Prompting Strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies) — Stratégies de raisonnement avancées.
*   [Agents.md](https://agents.md/) — Le standard pour la mémoire technique des agents IA.

---

## 🛠️ Personnalisation & Extensibilité

Vibrisse est conçu pour évoluer avec vos besoins. Vous pouvez facilement ajouter de nouvelles "mains" (Outils) à l'agent :
- **Outils Personnalisés** : Ajoutez vos propres fonctions Python pour interagir avec des APIs spécialisées ou des services locaux.
- **Serveurs MCP** : Connectez n'importe quel serveur Model Context Protocol pour donner instantanément de nouvelles capacités à Vibrisse.

Consultez le **[Guide de création d'outils dans AGENTS.md](./AGENTS.md#️-extension--ajouter-un-outil-tool)** pour un tutoriel étape par étape.

---

## 🎯 Roadmap
- [x] Interface Studio "Obsidian Glass" (Violet/Indigo)
- [x] Mode Terminal (TUI) haute performance
- [x] Intégration native MCP
- [x] Framework d'Évaluation (Ragas / LangSmith)
- [ ] Internationalisation complète (i18n) & Prompts en Anglais
- [ ] Multi-Agent Architecture (Orchestration spécialisée)
- [ ] Optimisation Contextuelle (Prompt Compression)
- [ ] Marketplace d'outils Vibrisse

---
*Vibrisse Agent : Parce que ton code mérite un interlocuteur à sa hauteur.*
