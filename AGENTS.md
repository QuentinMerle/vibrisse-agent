## 🧠 Philosophy: "Small models, Great tools."
Vibrisse empowers small local models (7B-8B) with high-precision tools and a robust reasoning structure.

## 🚀 Technical Overview
- **Backend**: FastAPI + LangGraph.
- **Frontend**: React (Obsidian Glass Aesthetic).
- **Core Strategy**: English prompts, Multilingual UI.
- **Swift Installation**: Zero-build strategy (pre-compiled `dist` folder included in repo to remove Node.js dependency for users).
- **Architecture**: Supervisor/Worker multi-agent system.

---

## 🏗️ Technical Deep Dives (RAG-Only)
- **[Architecture & Structure](docs/technical/architecture.md)**: Folders, DDD structure, tech stack.
- **[Hybrid Retrieval & RAG](docs/technical/retrieval.md)**: Surgical Grep, ChromaDB, Pruning logic.
- **[Reasoning & Agents](docs/technical/reasoning.md)**: Supervisor/Worker, Skills, Robust Parsing.
- **[Smart Personalization](app/services/core/system_discovery.py)**: Hardware discovery, Persona-based model strategy.

---

## 🎮 TUI Control Center
Vibrisse features an asynchronous TUI (`vibrisse_tui.py`) that acts as a command center.
- **Architecture**: Communicates with the FastAPI backend via `httpx`.
- **State Management**: Syncs global settings (model, path) across both Web and Terminal interfaces.
- **Commands**: `/model`, `/path`, `/scan`, `/stats`, `/tools`.

---

## ⚠️ Critical Watchpoints (DON'T BREAK THESE)

### 🎯 Router Calibration
The **router** (`app/agents/nodes/router.py`) has been hardened.
- Implements **Triple-Layer Robust Parsing** (Regex JSON -> Regex XML -> Keywords fallback).
- Any prompt change must be tested against all 3 routes.

### 👁️ Vision Strategy
- **Injection**: Vision descriptions are now injected directly into the last `HumanMessage` to force model attention.
- **Persistence**: `vision_description` is reset to `None` in `finalize_answer` to prevent "context ghosting" in future turns.

### 🌊 Thought Streaming
- Thoughts are streamed live during generation via `extract_thought` on the active buffer.
- The UI uses `ThinkingConsole` to render these thoughts separately from the answer.

### 🛠️ Runtime & Dependencies
- **Python**: Enforced version **3.12** for stability.
- **Node.js**: Only required for development (compiling `frontend/dist`).
- **Ports**: Default port is **8001**.

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
