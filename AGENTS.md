## 🧠 Philosophy: "Small models, Great tools."
Vibrisse empowers small local models (7B-8B) with high-precision tools and a robust reasoning structure. **Strategy: MCP-First.** We leverage the global Model Context Protocol ecosystem (Context7, GitHub, etc.) to give our agents "muscles" without rebuilding every connector.

## 🚀 Technical Overview
- **Backend**: FastAPI + LangGraph.
- **Frontend**: React (Obsidian Glass Aesthetic).
- **Core Strategy**: English prompts, Multilingual UI.
- **Swift Installation**: Zero-build strategy (pre-compiled `dist` folder included in repo).
- **Architecture**: Supervisor/Worker multi-agent system + MCP Hub.

---

## 🏗️ Technical Deep Dives (RAG-Only)
- **[Architecture & Structure](docs/technical/architecture.md)**: Folders, DDD structure, tech stack.
- **[Hybrid Retrieval & RAG](docs/technical/retrieval.md)**: Surgical Grep, ChromaDB, Pruning logic.
- **[Reasoning & Agents](docs/technical/reasoning.md)**: Supervisor/Worker, Skills, Robust Parsing.
- **[Observability & Evaluation](app/services/core/evaluation_service.py)**: Sovereign RAGAS scoring.
- **[MCP Integration](app/services/mcp/mcp_client.py)**: Manager for stdio-based MCP servers.

---

## 🎮 TUI Control Center
Vibrisse features an asynchronous TUI (`vibrisse_tui.py`) that acts as a command center.
- **Architecture**: Communicates with the FastAPI backend via `httpx`.
- **State Management**: Syncs global settings across both Web and Terminal interfaces.
- **Commands**: `/model`, `/path`, `/scan`, `/stats`, `/tools`.

---

## ⚠️ Critical Watchpoints (DON'T BREAK THESE)

### 🎯 Router Calibration
The **router** (`app/agents/nodes/router.py`) has been hardened.
- Implements **Triple-Layer Robust Parsing** (Regex JSON -> Regex XML -> Keywords fallback).
- Any prompt change must be tested against all 3 routes.

### 👁️ Vision Strategy
- **Injection**: Vision descriptions are now injected directly into the last `HumanMessage`.
- **Persistence**: `vision_description` is reset to `None` in `finalize_answer`.

### 🌊 Thought Streaming
- Thoughts are streamed live via `extract_thought` on the active buffer.
- The UI uses `ThinkingConsole` to render these thoughts separately.

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
- [x] Robust Tool Parsing (Triple-Layer).
- [x] **MCP Hub & Persistence** (Completed & Hardened).
- [x] **Sovereign Routing** (Industrialized & Bi-directional).
- [x] **Workspace Management** (Completed).
- [x] **Human-in-the-Loop** (Completed).
- [x] **Ghost Mode** (#ghost-mode). In-file directives for background tasks.
- [x] **Sovereign Routing** (Cloud-to-Local Savings).
- [x] **Thought Graph UI** (Completed).
- [x] **Architecture Mapping** (Completed).
- [x] **Vibrisse Update CLI** (Completed).
- [x] **Multi-Node & Custom LLM Support** (Completed).
- [ ] **VSCode Extension** (IDE Integration).
- [ ] **Multi-Node Support** (Enterprise).

---

## 👻 Ghost Mode
Ghost Mode allows you to control the agent directly from your code comments. It's perfect for quick refactors, documentation, or explanations without leaving your IDE.

### 🛠️ How to use
Add a comment containing the `@vibrisse:` tag followed by your instruction.

**Examples:**
- `# @vibrisse: add docstrings to all functions in this file`
- `// @vibrisse: refactor this loop to use a list comprehension`
- `/* @vibrisse: explain the security implications of this block */`

### 🔄 Workflow
1. **Detection**: Vibrisse's background watcher detects the tag in real-time.
2. **Execution**: A dedicated "Ghost Worker" processes the file and generates the modification.
3. **Applied**: The code is injected directly into the file, replacing the tag line.
4. **Notification**: You receive a system notification (macOS/Linux/Windows) once the task is done.

---
*Vibrisse AI: Small models, Great tools.*

