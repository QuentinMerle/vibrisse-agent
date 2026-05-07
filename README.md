# 🐱 Vibrisse Agent: The AI Assistant That Understands Your Code 🚀

[![English](https://img.shields.io/badge/lang-English-blue)](#)
[![Vibrisse - Studio Grade UI](https://img.shields.io/badge/UI-Studio--Grade-7b39ed)](file:///AGENTS.md)
[![Local First](https://img.shields.io/badge/Local--First-Ollama-10b981)](https://ollama.com)

> **"vi·brisse" (noun):** The long, stiff hairs growing around the face of many mammals, used as organs of touch. Whiskers.

Built on the conviction that **"Small models + Great tools = Professional performance"**, Vibrisse transforms local codebases into intelligent conversation partners. It senses patterns and navigates complex architectures with surgical precision.

<p align="center">
  <img src="./docs/assets/vibrisse-agent-ui.png" alt="Vibrisse Studio UI" width="100%">
</p>

---

## ✨ Key Highlights
- **Triple-Layer RAG**: Semantic search (Chroma), BM25, and **Surgical Grep** (ripgrep) for 100% technical precision.
- **Supervisor/Worker Architecture**: Specialized workers (Coder, Architect, Writer) for deep reasoning.
- **Smart Onboarding**: Real-time hardware discovery and persona-based setup (2-minute configuration).
- **Studio Interface**: An immersive "Obsidian Glass" web UI with real-time context monitoring.
- **Integrated Vision**: Visual context injection for UI analysis and multimodal reasoning.
- **Live Thought Streaming**: Real-time transparency of the agent's internal reasoning process.
- **Sovereign First**: Optimized for local-first intelligence via Ollama. No data leaves your machine by default.

---

## 🌐 Hybrid Model Support
While Vibrisse is built for **privacy-first local execution**, it also supports high-performance cloud providers for scenarios where you need extra speed or larger models:
- **Groq**: Extreme inference speed for real-time coding assistance.
- **OpenRouter**: Access to the world's most powerful models (Claude, GPT, Llama) via a single API.
- **Ollama Cloud**: Seamlessly scale your local Ollama experience to the cloud.

> [!NOTE]
> Unlike Ollama, these cloud providers are **proprietary SaaS services**. When using them, your prompts are processed on their servers. Use Ollama for 100% local sovereignty.

---

## 🚀 Getting Started

> [!IMPORTANT]
> **Compatibility Note**: Vibrisse Agent is optimized for **macOS**. It requires **Python 3.12** and **Ollama**.

### 🐱 User Mode (Swift Install)
Ideal for daily use. This installs Vibrisse as a global tool on your system.

```bash
# Run the one-liner installer
curl -sSL https://raw.githubusercontent.com/QuentinMerle/vibrisse-agent/main/install.sh | bash
```

Once installed, you can use these commands from anywhere:
- `vibrisse` : Launch the **Obsidian Glass** Web Studio.
- `vibrisse-tui` : Launch the **Control Center** in your terminal.
- `vibrisse update` : Update the agent to the latest version.

---

### 🛠️ Developer Mode (Source)
Ideal if you want to explore the code or contribute to the project.

```bash
# 1. Clone the repository
git clone https://github.com/QuentinMerle/vibrisse-agent.git
cd vibrisse-agent

# 2. Setup environment (Python 3.12)
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Frontend (Optional - only if you modify it)
cd frontend && npm install && npm run build
```

Launch in dev mode: `uvicorn app.main:app --reload --port 8001`

---

## ⌨️ Control Center (TUI)
Vibrisse comes with a powerful terminal interface for quick management. Launch it with `vibrisse --tui`.

| Command | Action |
| :--- | :--- |
| `/model [name]` | List or change the active LLM model |
| `/path [path]` | Change the target project directory |
| `/scan` | Re-trigger project analysis (onboarding) |
| `/stats` | View live system RAM and Ollama status |
| `/tools` | List all active tools and MCP servers |
| `/ui` | Open the Studio Web Interface |
| `/new` | Start a clean new discussion |

---

## 📚 Documentation
- **[Capabilities & Tools](docs/features/capabilities.md)**: What the agent can actually do.
- **[Security & Privacy](docs/features/security.md)**: How we protect your code.
- **[Technical Architecture](AGENTS.md)**: Deep dive into the graph and "Swift" strategy.
- **[Evolution Roadmap](ROADMAP.md)**: Where we are going next.

---
*Vibrisse AI: Small models, Great tools.*
