# 🗺️ Vibrisse Agent - Evolution Roadmap

This document tracks the long-term vision and specific ideas for evolving Vibrisse from a local assistant into a "Studio-Grade" engineering partner.

---

## 🧠 Intelligence & Architecture

### 1. Supervisor/Worker Refactoring (Completed ✅)
- **Goal**: Move from a monolithic graph to a multi-agent system.
- **Concept**: A "Supervisor" node analyzes the intent and dispatches tasks to specialized "Workers" (Expert Coder, Doc Maker, System Debugger).
- **Benefit**: Better reasoning depth and easier debugging of the agent's internal state.

### 2. Hybrid Retrieval: "Surgical Grep" (Completed ✅)
- **Goal**: Instant and exact code location.
- **Concept**: Integrated `ripgrep` (Rust) directly into the RAG pipeline.
- **Benefit**: 100% precision on keyword searches and near-zero latency for technical terms.

### 3. Studio-Lite Optimizations (Completed ✅)
- **Goal**: Performance and stability for local models.
- **Mechanism**: 
    - **Context Pruning**: Automated removal of headers and noise (20% token reduction).
    - **Robust Parsing**: Multi-layer (JSON/XML/Keyword) parsing for resilient tool execution.

### 4. Long-term Session Memory (Completed ✅)
- **Goal**: Conversations that survive server restarts.
- **Implementation**: Persistent thread storage in SQLite with full CRUD capabilities (List, Resume, Delete).

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

### 2. Update Mechanism (`vibrisse update`)
- **Goal**: Seamless updates for users.
- **Action**: A CLI command that performs `git pull`, updates dependencies, and rebuilds the frontend assets automatically.

### 3. Native Desktop Packaging
- **Goal**: A standalone application.
- **Tech**: Prototyping with **Tauri** (Rust) to wrap the React frontend and manage the Python backend as a sidecar process.

---

## 🛠️ Extensibility & Ecosystem

### 1. Vibrisse Tool Marketplace
- **Goal**: Community-driven capabilities.
- **Concept**: A directory of MCP servers and custom Python tools that can be "hot-loaded" into the agent.

### 2. Context Optimization
- **Goal**: Surgical project awareness.
- **Ideas**: Better support for very large monorepos, automated "Context Maps" of the project architecture.

---

## ⚙️ Maintenance & Hardening
- [x] **Python 3.12.4 Migration**: Performance and type-safety upgrade.
- [ ] **CI/CD Pipeline**: Automated testing for the router and tool execution nodes.
- [ ] **Ragas Industrialization**: Real-time evaluation dashboard in the Studio UI.

---
*Vibrisse AI: Small models, Great tools.*
