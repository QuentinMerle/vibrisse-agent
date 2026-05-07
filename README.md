# 🐱 Vibrisse Agent: The AI Assistant That Understands Your Code 🚀

[![English](https://img.shields.io/badge/lang-English-blue)](#)
[![Français](https://img.shields.io/badge/lang-Français-red)](file:///README_FR.md)
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
- **100% Local**: Sovereign intelligence via Ollama. No data leaves your machine.

---

## 🚀 Getting Started

> [!IMPORTANT]
> **Compatibility Note**: Vibrisse Agent is currently optimized and tested primarily for **macOS**. While it may work on Linux/Windows, native features (like the directory picker) and path handling are tailored for the Mac ecosystem.

### 🐍 Python Environment Tips
If you encounter `command not found: pip` on macOS, use:
- `python3 -m pip install ...`
- Always ensure your virtual environment is active: `source .venv/bin/activate`
- Or use the direct path: `./.venv/bin/python -m pip install ...`

1. **Prerequisites**: [Ollama](https://ollama.com/), Python 3.11+, Node.js 18+.
2. **Launch**:
```bash
git clone https://github.com/QuentinMerle/vibrisse-agent.git
cd vibrisse-agent

# One-command launch (Install & Start)
./vibrisse-cli.sh
```

---

## 📚 Documentation

Detailed documentation is available in the `docs/` folder:

- **[Capabilities & Tools](docs/features/capabilities.md)**: What the agent can actually do.
- **[Security & Privacy](docs/features/security.md)**: How we protect your code.
- **[Technical Architecture](AGENTS.md)**: Deep dive into the graph and multi-agent logic.
- **[Evolution Roadmap](ROADMAP.md)**: Where we are going next.

---

## ⌨️ Productivity Shortcuts
| Key | Action |
| :--- | :--- |
| `CMD + K` | Focus on input bar |
| `CMD + B` | Toggle sidebar (Slim Mode) |
| `CMD + N` | New clean discussion |

---
*Vibrisse AI: Small models, Great tools.*
