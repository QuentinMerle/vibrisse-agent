# 🗺️ Vibrisse Agent - Evolution Roadmap

This document tracks the long-term vision and specific ideas for evolving Vibrisse from a local assistant into a "Studio-Grade" engineering partner.

---

## 🧠 Intelligence & Architecture

### 1. Supervisor/Worker Refactoring (High Priority)
- **Goal**: Move from a monolithic graph to a multi-agent system.
- **Concept**: A "Supervisor" node analyzes the intent and dispatches tasks to specialized "Workers" (Expert Coder, Doc Maker, System Debugger).
- **Benefit**: Better reasoning depth and easier debugging of the agent's internal state.

### 2. Vibrisse "Lite" Mode
- **Goal**: Tailor the experience for small local models (7B/8B).
- **Features**:
    - **Prompt Compression**: Aggressive context pruning to stay within limited windows.
    - **Atomic Tasks**: Forced breakdown of complex requests into simple steps.
    - **Few-Shot Library**: Injecting task-specific examples to guide the model.

### 3. Long-term Session Memory
- **Goal**: Conversations that survive server restarts.
- **Implementation**: Persistent thread storage in SQLite/ChromaDB with the ability to "resume" a deep debugging session from days ago.

## 🚀 Onboarding & Personalization (Step 0)

### 1. Smart Onboarding Wizard
- **Goal**: Guide the user from the very first second.
- **Concept**: A setup screen that detects system resources (RAM, GPU) and asks for the user's **Persona** (Developer, Technical Writer, Data Analyst, Architect).
- **Features**:
    - **Resource-Aware Recommendations**: Suggest models based on available VRAM (e.g., Phi-3 for 8GB, Llama3-8B for 16GB, Llama3-70B for 64GB).
    - **Persona Tailoring**: Automatically pre-configure the system prompts and default "Skills" based on the selected role.
    - **Hardware Check**: Detect Ollama installation and download the best-fit model automatically if missing.

---

## 📦 Distribution & Developer Experience

### 1. "One-Liner" Global Installer
- **Goal**: `curl -fsSL https://vibrisse-studio.dev/install.sh | bash`
- **Features**:
    - Automatic `venv` creation and dependency syncing.
    - Global `vibrisse` command added to PATH.
    - Onboarding scan integrated into the installation flow.

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
*Vibrisse Studio: Pushing the boundaries of sovereign engineering.*
