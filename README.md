# 🐱 Vibrisse Agent: The AI Assistant That Understands Your Code 🚀

[![English](https://img.shields.io/badge/lang-English-blue)](#)
[![Vibrisse - Studio Grade UI](https://img.shields.io/badge/UI-Studio--Grade-7b39ed)](#)
[![Local First](https://img.shields.io/badge/Local--First-Ollama-10b981)](https://github.com/ollama/ollama)
[![MCP Hub](https://img.shields.io/badge/MCP-Hub--First-orange)](https://github.com/modelcontextprotocol/spec)
[![Multi-Agent](https://img.shields.io/badge/Architecture-Multi--Agent-ff69b4)](#)
[![Privacy](https://img.shields.io/badge/Privacy-100%25--Local-green)](#)
[![Zero-Build](https://img.shields.io/badge/Install-Zero--Build-00c1d4)](#)

> **"vi·brisse" (noun):** The long, stiff hairs growing around the face of many mammals, used as organs of touch. Whiskers.

Built on the conviction that **"Small models + Great tools = Professional performance"**, Vibrisse transforms local codebases into intelligent conversation partners. It senses patterns and navigates complex architectures with surgical precision.

<p align="center">
  <img src="./docs/assets/vibrisse-agent-ui.png" alt="Vibrisse Studio UI" width="100%">
</p>

---

## 💎 Why Vibrisse? (The Local AI Reference)

Vibrisse is not just another LLM wrapper. It's a **Sovereign Agent Framework** designed for the post-cloud era:
1. **Privacy as a Feature**: Your code never leaves your machine unless you explicitly allow it via Sovereign Routing.
2. **Efficiency First**: We prove that 7B-8B models can outperform GPT-4 on technical tasks when given the right "muscles" (MCP Tools + Surgical RAG).
3. **Studio-Grade UX**: A developer tool should look as good as it works. "Obsidian Glass" isn't just a style; it's a focus-oriented environment.

---

## ✨ Studio Highlights

### ⚖️ Sovereign Routing (Smart Offloading)
Vibrisse is a **Hybrid Intelligence** orchestrator. It intelligently arbitrates between local-first execution (Ollama) and high-capacity cloud models (Groq, OpenRouter) based on task complexity. 
- **Cost Efficiency**: Automatically offloads routine technical tasks (file listing, grep) to local models.
- **Privacy Control**: You decide exactly when data leaves your machine via a dedicated Sovereign Toggle.

### 🔌 MCP-Native Hub
Stop rebuilding what already exists. Vibrisse acts as a **centralized MCP Client**, allowing you to plug in any tool from the global Model Context Protocol ecosystem:
- **Persistent Hub**: Connect GitHub, Linear, Slack, or Postgres once; use them across every session.
- **Dynamic Tooling**: Your agent gains "muscles" in real-time as you add new servers.

### 🌊 Obsidian Glass Interface
A premium, immersive Studio experience designed for deep work:
- **Thought Graph**: Real-time visualization of the agent's reasoning path.
- **Thinking Console**: Live thought streaming to understand the *why* behind every action.
- **Surgical RAG**: Triple-layer retrieval combining Semantic Search, BM25, and high-precision Ripgrep.

---

## 🎮 What Vibrisse Can Do (Capabilities)

Vibrisse is designed to be part of your workflow, not another window you have to manage.

### 👻 Ghost Mode (IDE Directives)
You don't even need to open the UI. Add tags directly in your code comments:
- **`// @vibrisse: refactor this function`**: The agent will detect the tag in the background and perform the task.
- **`# @vibrisse: explain this logic`**: Get technical explanations injected right where you need them.

### 🏷️ Precision Mentions
In the chat, use **triggers** to give the agent surgical context:
- **`@` Mention Files/Folders**: Type `@` followed by a filename to inject its full content or path into the conversation.
- **`/` Mention Folders**: Type `/` to suggest specific directories for the agent to explore or list.

### 🛠️ Professional Tooling
- **Search Everything**: Ask "Where is the API key defined?" and Vibrisse will use **Ripgrep** for 100% accurate results.
- **Web Research**: Integrated web search via Tavily. **No need to touch .env files**—simply paste your API key in the Studio Settings.
- **MCP Ecosystem**: Connect servers to manage **Linear tickets**, **GitHub PRs**, or **Postgres databases** directly from the chat.
- **Smart Offloading**: If you ask a simple question like "List files in src", Vibrisse will automatically use a **Local Model** to save you Cloud tokens.

---

## 🚀 Getting Started

> [!IMPORTANT]
> **Compatibility**: Cross-platform (**macOS**, **Windows/WSL2**, **Linux**). Requires **Python 3.12** and **Ollama**.

### 🐱 User Mode (Swift Install)
Installs Vibrisse as a global command on your system.

**macOS / Linux:**
```bash
# Run the branded one-liner installer
curl -sSL https://agent.vibrisse-studio.dev/install.sh | bash
```

**Windows (PowerShell):**
```powershell
# Run the branded one-liner installer
irm https://agent.vibrisse-studio.dev/install.ps1 | iex
```

**Commands:**
- `vibrisse` : Launch the Web Studio (http://localhost:8001).
- `vibrisse-tui` : Launch the terminal Control Center.
- `vibrisse update` : Sync latest features and dependencies.

### 🛠️ Developer Mode (Source)
```bash
git clone https://github.com/QuentinMerle/vibrisse-agent.git
cd vibrisse-agent
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Dev server (Backend):
uvicorn app.main:app --reload --port 8001

# Dev server (Frontend - Optional):
cd frontend && npm install && npm run dev
```

---

## 🤝 Contributor Hub

Vibrisse is built for and by the local AI community. Whether you are an LLM enthusiast, a React wizard, or a Python architect, your help is welcome!

- **Add a Worker**: Create specialized agents for specific languages or tasks.
- **Connect MCP Servers**: Help us build the largest hub of local-first tools.
- **Polish the UI**: Improve the Obsidian Glass experience.

Check out our **[Contribution Guide](CONTRIBUTING.md)** to get started!

---

## 📚 Documentation Hub

Explore the full potential of the Vibrisse ecosystem:

### 🌟 Features & Usage
- **[Capabilities](docs/features/capabilities.md)**: Explore what the agent can actually do (File I/O, Search, MCP).
- **[Sovereign Routing](docs/technical/architecture.md#sovereign-routing)**: How the hybrid local/cloud arbitration works.
- **[Ghost Mode](AGENTS.md#ghost-mode)**: Control the agent via in-file `@vibrisse:` directives.
- **[Security & Privacy](docs/features/security.md)**: Our commitment to local-first data sovereignty.

### 🏗️ Technical Deep Dives
- **[Architecture Overview](docs/technical/architecture.md)**: DDD structure, LangGraph flow, and services.
- **[Dynamic Personas](docs/technical/dynamic_personas.md)**: Alignment of Wizard-selected personas with specialized system prompts.
- **[Inference Engines](docs/technical/inference_engines.md)**: Guide to Ollama, Custom (vLLM/LM Studio), and Cloud providers.
- **[Hybrid Retrieval (RAG)](docs/technical/retrieval.md)**: How we achieve 100% precision with surgical grep.
- **[Reasoning & Agents](docs/technical/reasoning.md)**: Supervisor/Worker patterns via [**langchain-ai/langgraph**](https://github.com/langchain-ai/langgraph) and robust parsing.
- **[Setup & Hardware](docs/technical/setup.md)**: Requirements for optimal performance.

### 🗺️ Project State
- **[Evolution Roadmap](ROADMAP.md)**: Future vision and upcoming features.
- **[Agent Strategy](AGENTS.md)**: The "Small models, Great tools" philosophy in detail.
- **[Testing Protocols](docs/technical/testing.md)**: How we ensure stability and reliability.

---

## 🎮 TUI Quick Commands
| Command | Action |
| :--- | :--- |
| `/model` | List or change active LLM models |
| `/path` | Switch target workspace/project |
| `/scan` | Force architectural re-analysis |
| `/tools` | List connected MCP servers and tools |
| `/stats` | Real-time RAM and Ollama health |

---
*Vibrisse AI: Small models, Great tools.*

_Proudly developed in Beauce, Québec 🇨🇦. Interested in local AI sovereignty? Let's connect!_