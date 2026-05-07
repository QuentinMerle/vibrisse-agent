# Vibrisse Agent - Context & Guidelines

This file serves as the technical memory for AI agents. It defines the core architecture and critical standards.

## 🧠 Philosophy: "Small models, Great tools."
Vibrisse empowers small local models (7B-8B) with high-precision tools and a robust reasoning structure.

## 🚀 Technical Overview
- **Backend**: FastAPI + LangGraph.
- **Frontend**: React (Obsidian Glass Aesthetic).
- **Core Strategy**: English prompts, Multilingual UI.
- **Architecture**: Supervisor/Worker multi-agent system.

---

## 🏗️ Technical Deep Dives (RAG-Only)
For detailed information on specific modules, consult these files:
- **[Architecture & Structure](docs/technical/architecture.md)**: Folders, DDD structure, tech stack.
- **[Hybrid Retrieval & RAG](docs/technical/retrieval.md)**: Surgical Grep, ChromaDB, Pruning logic.
- **[Reasoning & Agents](docs/technical/reasoning.md)**: Supervisor/Worker, Skills, Robust Parsing.
- **[Smart Personalization](app/services/core/system_discovery.py)**: Hardware discovery, Persona-based model strategy.
- **[Observability & Evals](app/services/core/evaluation_service.py)**: Ragas local Judge pattern.

---

## 🛠️ Tool Inventory (Summary)
- **`list_dir` / `read_file` / `grep_search`**: System exploration.
- **`write_file`**: Maker Mode.
- **`run_terminal_command`**: Approved system execution.
- **`web_search`**: Tavily/DDG integration.
- **`Vision`**: Image analysis.

---

## ⚠️ Critical Watchpoints (DON'T BREAK THESE)

### 🎯 Router Calibration
The **router** (`app/agents/nodes/router.py`) is the most sensitive component.
- Implements **Robust Parsing** (JSON -> XML -> Keywords).
- Any prompt change must be tested across all 3 routes.

### 🍎 Environment & OS
- **OS**: Primarily tested on **macOS**.
- **Python**: Use `python3 -m pip` instead of `pip` if path issues occur.
- **Venv**: Always target `./.venv/bin/python` for tool installations to ensure persistence.

### 🚧 Dependencies
- Updating `langgraph` or `langchain` is **High Risk** due to silent breaking changes in tool returns.

---

## 📋 Roadmap & State
- [x] Multi-Agent Architecture (Supervisor/Worker).
- [x] Triple-Layer Retrieval (Grep/Semantic/BM25).
- [x] Context Persistence (SQLite).
- [x] Studio UI (Obsidian Glass).
- [ ] Context Compression (Advanced).
- [ ] Vibrisse "Lite" (Rust/Standalone).

---
*Vibrisse AI: Small models, Great tools.*
