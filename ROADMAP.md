# 🗺️ Vibrisse Agent - Evolution Roadmap

This document tracks the long-term vision and specific ideas for evolving Vibrisse from a local assistant into a "Studio-Grade" engineering partner.

---

## 🎯 V0.1 Launch Target (Focus Actuel)
Pour l'ouverture au public, nous nous concentrons sur ces 4 piliers :
- [x] **Thought Graph UI** : Visualisation réactive du raisonnement (React Flow).
- [x] **Architecture Context Mapping** : Génération d'un `project_map.json` pour une conscience repo-scale.
- [x] **Vibrisse Update CLI** : Commande `vibrisse update` pour une maintenance simplifiée.
- [x] **Cross-Platform Hardening** : Validation complète Mac, Windows (WSL2/Native) et Linux.

---

## 🧠 Intelligence & Architecture

### 1. Supervisor/Worker Refactoring (Completed ✅)
- **Goal**: Move from a monolithic graph to a multi-agent system.
- **Concept**: A "Supervisor" node dispatches tasks to specialized "Workers".
- **Benefit**: Better reasoning depth and easier debugging.

### 2. Triple-Layer Robust Parsing (Completed ✅)
- **Goal**: Resilient tool execution for small models (7B-8B).
- **Mechanism**: Regex JSON -> Regex XML -> Keywords fallback.
- **Benefit**: Zero-fail tool calling even with models prone to formatting errors.

### 3. Long-term Session Memory (Completed ✅)
- **Goal**: Conversations that survive server restarts.
- **Implementation**: Persistent thread storage in SQLite with full CRUD capabilities.

## 🚀 Onboarding & Personalization (Step 0)

### 1. Smart Onboarding Wizard (Completed ✅)
- **Goal**: Guide the user from the very first second.
- **Implementation**: `SystemDiscoveryService` tracks RAM/VRAM and provides model recommendations.
- **Features**:
    - **Resource-Aware Recommendations**: High/Mid/Low tiers.
    - **Persona-Based Models**: Developer, Data, Writer, Architect profiles.
    - **Asynchronous Pulling**: Real-time background installation of LLMs.
    - **Workspace Discovery**: Automated project path configuration.
    - **Session Persistence**: Backend-level state tracking (no more recurring setup).

---

## 📦 Distribution & Developer Experience

### 1. "One-Liner" Global Installer (Completed ✅)
- **Goal**: `curl -fsSL https://vibrisse-studio.dev/install.sh | bash`
- **Implementation**: `install.sh` automates cloning, venv setup, npm install, and alias creation.

### 2. Update Mechanism (`vibrisse update`) (Completed ✅)
- **Goal**: Seamless updates for users.
- **Action**: A CLI command that performs `git pull`, updates dependencies, and rebuilds the frontend assets automatically.

### 3. Native Desktop Packaging
- **Goal**: A standalone application.
- **Tech**: Prototyping with **Tauri** (Rust) to wrap the React frontend and manage the Python backend as a sidecar process.

## 🏗️ The MCP-First Studio (Active Focus 🚀)

### 1. The MCP Hub & Persistence (Completed ✅)
- **Goal**: Stop rebuilding what already exists.
- **Concept**: A centralized manager for MCP servers (Context7, GitHub, Slack).
- **Action**: Implemented persistent storage in SQLite for MCP configurations per workspace with auto-recovery on startup. Hardened for small model compatibility.

### 2. Workspace Intelligence & HITL (Completed ✅)
- **Goal**: Professional project isolation and safety.
- **Concept**: User approval for destructive tools and project-level settings.
- **Action**: Implement LangGraph `interrupts` and project-specific config files.

### 3. Smart Offloading (Sovereign Routing) (Industrialized 🚀) (Completed ✅)
- **Goal**: Optimize token usage and intelligence by diverting tasks.
- **Mechanism**: Sovereign Sentinel analyzes query complexity and proposes/automates switches between Local and Cloud.
- **Benefit**: Bi-directional routing, user-controlled via settings toggle.

### 4. Ghost Mode (In-File Directives) (Completed ✅)
- **Goal**: Trigger agent actions directly from code comments.
- **Mechanism**: WatcherService detects `@vibrisse:` tags and triggers background edits.
- **Benefit**: Seamless IDE integration and zero context-switching.

---

## 🖼️ Future Vision: Multimodal & Specialized Workers

### 1. The Designer Worker (Local Image Generation)
- **Goal**: Generate high-fidelity visual mockups using local diffusion models without bloating the core agent.
- **Concept**: Use an MCP server connected to local rendering engines (ComfyUI, DrawThings) running models like **Flux.1** combined with a specialized **"UI/UX Web Design" LoRA** (Low-Rank Adaptation) to ensure professional, pixel-perfect UI generation.
- **Workflow**: The `Router` delegates visual requests to a specialized `Designer` LLM, which crafts technical image prompts and calls the MCP server. The result is seamlessly displayed in the chat via Markdown.

### 2. The Stitch Worker (UI/UX Mockup & Wireframing)
- **Goal**: Generate conceptual wireframes and UI/UX mockups *before* writing any production code (acting as a Figma/Sketch alternative).
- **Concept**: A specialized LLM that translates user needs into visual architectures (using Mermaid, Excalidraw JSON, SVG, or interacting with a Figma MCP).
- **UI Integration**: The conceptual mockup is intercepted and rendered live in the chat, allowing the user to validate the information architecture before handing it off to the Coder Worker.

---

## 🎨 Visual & UX Excellence

### 1. Thought Graph UI (Completed ✅)
- **Goal**: "Studio-Grade" observability.
- **Concept**: A reactive visual graph showing the agent's journey in real-time.

### 2. Architecture Context Mapping (Completed ✅)
- **Goal**: Surgical project awareness for large repos.
- **Concept**: Background generation of a `project_map.json` summarizing the architecture.

---

## 💻 IDE Integration

### 1. Vibrisse for VSCode
- **Goal**: Bring the power of Vibrisse where the code is.
- [x] **Multi-Node & Custom LLM Support** (Active Focus).
- [ ] **VSCode Extension** (IDE Integration).

### 🚀 V2: Collaborative & Enterprise (Future Vision)
- [ ] **Semantic Caching Layer**: Avoid redundant LLM calls by caching similar queries in a vector store.
- [ ] **Centralized Vector Store**: Support for remote ChromaDB/Qdrant servers for team-wide code indexing.
- [ ] **Enterprise Persistence**: Migration from SQLite to PostgreSQL for multi-user conversation state.
- [ ] **CI/CD Indexing**: Automated project mapping triggered by Git hooks.
- [ ] **Headless Agent Deployment**: Decouple the reasoning engine from the local machine for GPU offloading.

---

## ⚙️ Maintenance & Hardening
- [x] **Python 3.12.4 Migration**: Performance and type-safety upgrade.
- [x] **Context Compression & Pruning**: Automated removal of noise in RAG.
- [x] **Recursion & Stability Hardening**: Graph recursion limit increased to 50 for complex tasks.
- [x] **Vibrisse Update CLI**: `vibrisse update` command to sync git, deps, and frontend.
- [x] **Ragas Industrialization**: Real-time evaluation dashboard in the Studio UI.

---
*Vibrisse AI: Small models, Great tools.*
