# 🐱 Vibrisse Agent: The AI Assistant That Understands Your Code 🚀

[![English](https://img.shields.io/badge/lang-English-blue)](#)
[![Français](https://img.shields.io/badge/lang-Français-red)](file:///README_FR.md)
[![Vibrisse - Studio Grade UI](https://img.shields.io/badge/UI-Studio--Grade-7b39ed)](file:///AGENTS.md)
[![Local First](https://img.shields.io/badge/Local--First-Ollama-10b981)](https://ollama.com)
[![MCP Powered](https://img.shields.io/badge/MCP-Extensible-yellow)](https://modelcontextprotocol.io)

**Vibrisse Agent** is a "Studio-Grade" agentic AI assistant designed by **Vibrisse Studio**. Born from the curiosity of a web developer turned AI engineer, this tool transforms your local codebases into intelligent conversation partners. Built on a **LangGraph** architecture and optimized for **100% local** execution, it embodies the expertise and vision of our **Vibrisse AI** service.

<p align="center">
  <img src="./docs/assets/vibrisse-agent-ui.png" alt="Vibrisse Studio UI" width="100%">
</p>

---

## ✨ Key Highlights (The Studio Experience)

### 📊 Observability & Evaluation (Ragas)
Vibrisse integrates the **RAGAS** framework to evaluate faithfulness (anti-hallucination) and answer relevance in real-time.

### 🎨 Dual Control Interface
*   **Studio Web UI (Cockpit)** : An immersive "Obsidian Glass" interface featuring an intelligent sidebar, real-time context monitoring, and high-definition Markdown rendering.
*   **Hacker TUI (Terminal)** : A blazing-fast textual interface in indigo purple to control the agent without leaving your terminal.
*   **Total Fluidity** : Keyboard shortcuts (`CMD+K`, `CMD+B`), skeleton loading, and precision animations.

### 🧠 Contextual Intelligence
*   **Hybrid RAG** : Vector search (semantic) coupled with BM25 search (keywords) for surgical precision on your code.
*   **Project Onboarding** : Automatic architecture scan, reading manifests (`README.md`, `CONTEXT.md`) for immediate project awareness.
*   **Modular Skills** : Expertise instructions isolated in Markdown files (`app/agents/skills/`), allowing you to modify agent behavior without changing a single line of code.

### 🔌 Extensibility (MCP)
*   **Model Context Protocol** : Vibrisse is natively compatible with MCP servers. Connect your agent to GitHub, Linear, Slack, or your own custom tools in seconds.
*   **Tool Execution Control** : You maintain full control with explicit validation (Human-in-the-Loop) before every system command execution.

---

## 🚀 Quick Start

### Prerequisites
*   [Ollama](https://ollama.com/) installed and running.
*   Python 3.11+
*   Node.js & npm (for the frontend)

### Installation & Launch
```bash
# Clone the project
git clone https://github.com/QuentinMerle/vibrisse-agent.git
cd vibrisse-agent

# Automatic Launch (Onboarding & Install)
./vibrisse-cli.sh --onboard

# Launch Studio Mode (Web UI)
./vibrisse-cli.sh

# Launch Hacker Mode (Terminal TUI)
./vibrisse-cli.sh --tui
```

---

## ⚙️ Configuration (Environment Variables)

Vibrisse is configured via a `.env` file. Key variables:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `TARGET_PROJECT_PATH` | `.` | Path to the codebase to analyze |
| `LLM_PROVIDER` | `ollama` | `ollama` (local), `ollama_cloud`, `groq` or `openrouter` |
| `LLM_MODEL` | `gemma4:e2b` | Primary model for chat |
| `ENABLE_WEB_SEARCH` | `true` | Allows the agent to search the web (Tavily/DDG) |
| `TAVILY_API_KEY` | - | API Key for web search (optional, falls back to DDG) |
| `RAGAS_MODEL` | `llama3:8b` | Model used for evaluation judging (8B+ recommended) |

---

## ⌨️ Productivity Shortcuts

| Key | Action |
| :--- | :--- |
| `CMD + K` | Instant focus on input bar |
| `CMD + B` | Toggle sidebar (Slim Mode) |
| `CMD + N` | Start a new clean discussion |
| `/ui` (TUI) | Switch from terminal to Web interface |

---

## 🛡️ Security & Privacy

Vibrisse is built with a **Security-by-Design** approach to protect your code and data.

*   **Local-First & Sovereignty** : If using Ollama, no line of your code or conversation leaves your machine. Vibrisse works perfectly offline.
*   **Human-in-the-Loop (HITL)** : The agent is forbidden from executing system commands (`run_terminal_command`) without explicit validation from you in the UI.
*   **Secret Scrubbing** : An automatic filtering system masks API keys, tokens, and passwords that might accidentally appear in agent logs.
*   **Data Isolation** : Your chat history and vector indices are stored locally in the `/data` folder, which is strictly excluded from Git tracking.

---

## 🏗️ Architecture & 📂 Structure

Vibrisse follows a modular architecture to separate intelligence (LLM) from infrastructure (API/UI).

```text
.
├── app/                # Backend FastAPI & Agentic Logic (LangGraph)
├── data/               # Vector indices & Local databases
├── docs/               # Detailed documentation (Business, Tech, Roadmap)
├── frontend/           # React Studio Interface (Vite + Vanilla CSS)
├── AGENTS.md           # Instructions & Technical Memory for AIs
├── DESIGN.md           # Design System "Obsidian Glass" (UI Source of Truth)
├── README.md           # This documentation
└── vibrisse-cli.sh     # Unified Launcher (Backend + Frontend)
```

---

## 🚨 Pitfalls & Gotchas

### The Router: The Fragile Heart
The **router** (`app/agents/nodes/router.py`) is the critical component that decides how to process every message. Calibrating it is a **long and iterative** process. Refer to the test table in `AGENTS.md` before making any changes.

### ⚠️ Upgrading LangChain?
The project uses cutting-edge features from LangGraph and LangChain. Version upgrades can introduce **silent breaking changes** (e.g., changes in tool return formats). Update one package at a time and test rigorously.

---

## ⚖️ Disclaimer

Vibrisse Agent is an experimental tool using Large Language Models (LLMs) to generate and execute code. While it integrates security mechanisms (HITL), the user remains solely responsible for the commands validated and the modifications made to their system. Vibrisse Studio cannot be held responsible for any data loss or damage caused by the use of this assistant.

---

## 🤖🤝🧠 The Vibrisse Spirit: AI-Human Alliance

Vibrisse is not just a tool; it's a study in collaboration. We believe AI excels at algorithms and parsing, while humans bring systemic intuition. 

> *Dev note: Vibrisse was designed by an AI and a human working in tight-knit synergy. This partnership is at the core of every line of code.*

---

## 📚 Sources & Inspiration
*   [IBM Technology](https://www.youtube.com/@IBMTechnology) — For deep architectural insights.
*   [Google Cloud: What is Prompt Engineering?](https://cloud.google.com/discover/what-is-prompt-engineering) — Foundational principles.
*   [Gemini API: Prompting Strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies) — Advanced reasoning and prompting techniques.
*   [Agents.md](https://agents.md/) — The standard for AI agent technical memory.

---

## 🛠️ Customization & Extensibility

Vibrisse is designed to grow with your needs. You can easily add new "Hands" (Tools) to the agent:
- **Custom Tools** : Add your own Python functions to interact with specialized APIs or local services.
- **MCP Servers** : Connect any Model Context Protocol server to instantly give Vibrisse new capabilities.

Refer to the **[Tool Creation Guide in AGENTS.md](./AGENTS.md#️-extension--ajouter-un-outil-tool)** for a step-by-step tutorial.

---

## 🎯 Roadmap
- [x] Studio Interface "Obsidian Glass" (Purple/Indigo)
- [x] High-performance Terminal Mode (TUI)
- [x] Native MCP Integration
- [x] Evaluation Framework (Ragas / LangSmith)
- [ ] Native Packaging (Electron / Tauri)
- [ ] Full Internationalization (i18n) & English Prompts
- [ ] Context Optimization (Prompt Compression)
- [ ] Vibrisse Tool Marketplace

---
*Vibrisse Agent: Because your code deserves a partner at its level.*
