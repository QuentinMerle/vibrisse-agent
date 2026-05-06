# Vibrisse Agent - Context & Guidelines

This file serves as the technical memory for AI agents working on this project. It defines the architecture, standards, and current state of the system.

## 🧠 Philosophy & Core Concept

**"Small models, Great tools."**  
Vibrisse is built on a core conviction: a "small" local model (7B-8B), when equipped with high-precision tools and a robust reasoning structure, can outperform larger, generic cloud models for specific engineering tasks. 

> **Vibrisse (Concept)**: Named after the sensory whiskers of cats, these surgical tactile organs allow navigation in complex environments with extreme precision. The agent acts as the tactile sensory organ for your codebase.

Our goal is to demonstrate that **sovereignty and performance** are not mutually exclusive. By providing the LLM with a "Studio-Grade" cockpit and surgical access to the codebase, we transform a simple chatbot into a professional engineering partner.

## 🚀 Technical Overview

**Vibrisse Agent** is an agentic AI assistant designed by **Vibrisse Studio** for **Vibrisse AI** engineering. It interacts with local codebases via a graph-based architecture (LangGraph) and a modern "Obsidian Glass" interface (React).

### Tech Stack
- **Backend**: FastAPI (Python 3.11+)
- **Agentic Logic**: LangGraph (LangChain ecosystem).
    - *Why?* We chose LangGraph for its ability to handle cyclic logic and fine-grained state management, which is essential for multi-step debugging and tool execution loops.
- **Frontend**: React + Vite + Vanilla CSS (Obsidian Glass Aesthetic).
- **Vector DB**: ChromaDB (for RAG).
- **Protocol**: MCP (Model Context Protocol) for tool extensibility.

### Interfaces
- **Web UI**: React + Vite (Studio Cockpit Mode).
    - *Aesthetics*: "Obsidian Glass" with custom **VibrisseAvatar** (dynamic cat ears and whiskers that react to thinking states).
- **TUI (Terminal)**: Python Rich + Prompt Toolkit (Hacker Mode).
- **CLI**: Unified `vibrisse-cli.sh` script for mode management.

---

## 🏗️ Architecture

### Backend (`app/`)
The backend follows a Domain-Driven Design (DDD) light structure:
- `app/agents/`: Agentic logic.
    - `graph.py`: State graph definition.
    - `nodes/`: Isolated graph nodes (`vision`, `retrieval`, `generation`, `tool_execution`).
- `app/services/`: Business logic layer.
    - `llm/`: Factory and model-related services.
    - `rag/`: Indexing and vector storage management (ChromaDB + BM25).
    - `mcp/`: Client for connecting external tool servers.
    - `core/`: Transversal services (SSE streaming, onboarding manifest, watchers, evaluation/Ragas).
- `app/schemas/`: Centralized Pydantic definitions.

### 🛠️ Tool Inventory (Capabilities)
The agent is equipped with a toolset to interact with the system:
- **`list_dir`**: Explore project structure.
- **`read_file`**: Surgical file reading (complementary to RAG).
- **`grep_search`**: Exact search (Regex/Terms) within the codebase.
- **`write_file`**: Create and update files (Maker Mode).
- **`run_terminal_command`**: Execute system commands (**Mandatory HITL**).
- **`web_search`**: Access real-time data via Tavily/DuckDuckGo.
- **`Vision Analysis`**: Native capacity to analyze images (screenshots, diagrams) via multimodal models.

### 🧠 Reasoning Engine

1. **Manifest Generation (Onboarding)**:
    At startup, `onboarding_service` scans `TARGET_PROJECT_PATH` to identify the stack (Docker, Python, Node, etc.). This manifest is injected into the system prompt to give the agent immediate "project awareness".
2. **Hybrid Retrieval Architecture**:
    Vibrisse combines two engines via `rank_bm25`:
    - **Dense (ChromaDB)**: For semantic and conceptual meaning.
    - **Sparse (BM25)**: For exact term matching (e.g., function names, IDs).
    - *Why?* Semantic search is great for "What is this about?", but BM25 is essential for "Find the function `on_click_handler`".

3. **Safety Ingestion Shield (Resource Management)**:
    To prevent memory exhaustion (swapping) during large project indexing, Vibrisse implements:
    - **Batch Processing**: Files are loaded and indexed in small groups (50 files) to keep RAM usage constant.
    - **Size Filtering**: Individual files larger than 1MB are automatically skipped from the vector index.
    - **Intelligent Exclusions**: Common heavy folders (`node_modules`, `.next`, `dist`, `build`, etc.) and hidden directories are ignored by default.

4. **Double-Pass Reasoning (Expert Review)**:
    Every complex technical response passes through an `expert_review_node`. A second LLM analyzes the draft to ensure technical excellence and adherence to standards.
4. **SSE Streaming Protocol**:
    All agent -> client communication uses `StreamService`. Events are typed: `token`, `thought`, `status`, `tool_calls`.
5. **History Merging**:
    The backend history API (`threads.py`) includes a **Consecutive Message Merger** to ensure that multi-step reasoning turns appear as single, coherent bubbles in the UI upon reload, matching the live streaming experience.

### 🧠 Reasoning System & Prompts

Vibrisse uses a hybrid approach for its instructions:

1. **Modular Skills (`app/agents/skills/`)**: 
   Domain expertise is stored in independent Markdown files. 
   - `code_expert.md`: Analysis and code generation.
   - `tool_expert.md`: Tool usage guide.
   - `orchestrator.md`: Planning and synthesis logic.
   - *Advantage*: We can modify the agent's "knowledge" without touching Python code. Loaded via `utils.load_skill()`.

2. **English Core Strategy**:
   All system prompts and skills are written in **English**.
   - *Why?* Most LLMs (even open-source ones) are trained on predominantly English datasets. They follow instructions more precisely and generate higher-quality code when prompted in English. The UI remains multilingual via `react-i18next`.

3. **Thinking Tags & Reducer**:
   We use `<thought>` tags to extract reasoning. To ensure a clean experience, we've implemented a **Custom State Reducer** for thoughts. It allows accumulating thoughts during a turn but triggers a `__RESET__` at the start of each new user intent, ensuring the ThinkingConsole only shows relevant information for the current task.

4. **The Router: The Air Traffic Controller**:
   The `router.py` node analyzes intent and chooses between 3 paths:
   - `vectorstore`: Triggers RAG on local code.
   - `web_and_tools`: Triggers the autonomous agent (Google, Terminal, MCP).
   - `direct_response`: For greetings or general knowledge.

### 📊 Technical Observability (Evals)

Vibrisse implements a **100% Local** evaluation pipeline via Ragas:
1. **LocalJSONJudge Pattern**: To counter the verbosity of local models (`llama3:8b`), the judge is encapsulated in a class inheriting from `BaseChatModel`. It intercepts outputs, extracts JSON via Regex, and ensures format compatibility with Ragas.
2. **Dynamic Model Injection**: Judge and embedding models are injected dynamically from `.env` during evaluation to avoid global configuration conflicts.

---

## ⚠️ Critical Watchpoints

### 🎯 Router Calibration (`app/agents/nodes/router.py`)

The **router** is the most sensitive component. It makes the initial decision that drives the entire chain.

**Learnings:**
- Router calibration is a **long and iterative** process via prompting. Imprecise wording sends requests to the wrong node, leading to silent failures.
- **Local models** (Ollama) are particularly sensitive: a prompt that is too long or poorly structured can cause invalid JSON output that the Pydantic parser will reject.

### 🚧 Warning: LangChain/LangGraph Upgrades

> **⚠️ HIGH RISK**: Updating `langchain-core`, `langgraph`, or `langchain-community` can cause **silent regressions**. Always update one package at a time and test all 3 router routes.

---

## 📋 Current State & Roadmap
- [x] **Structure**: Backend and Frontend refactoring complete.
- [x] **UX/UI Studio**: Slim Sidebar, Shortcuts, Welcome Screen, and Skeletons implemented.
- [x] **Internationalization (i18n)**: English Core prompts and Multilingual UI.
- [ ] **Multi-Agent Architecture**: Transition to "Supervisor/Worker" structure.
- [x] **Context Persistence**: Cache system for manifest and project path.
- [x] **Evaluation Framework**: Local RAG precision measurement (Ragas).

---

## 📦 Distribution & Maintenance Strategy

Vibrisse uses a **Hybrid Infrastructure** to balance accessibility and sovereignty:

1. **One-Liner Installer (`install.sh`)**:
   - Hosted on **Vercel** (`vibrisse-studio.dev`).
   - Automates environment isolation (venv), dependency syncing, and shell alias registration (`vibrisse` command).
2. **Update Mechanism**:
   - Maintenance is handled via `vibrisse update` (planned).
   - This command pulls the latest core from **GitHub** and re-triggers the onboarding/sync process.
3. **Data Sovereignty**:
   - While the landing page and installer are cloud-hosted, **100% of the logic and data** (LLM calls, embeddings, file access) remains strictly on the user's local machine.

---

## 🔑 Useful Commands
- **Launch Web UI**: `./vibrisse-cli.sh`
- **Launch TUI**: `./vibrisse-cli.sh --tui`
- **Dev Mode (Front)**: `cd frontend && npm run dev`
