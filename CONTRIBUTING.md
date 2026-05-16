# 🤝 Contributing to Vibrisse Agent

First off, thank you for considering contributing to Vibrisse! It's people like you who make Vibrisse a reference for local AI agents.

## 🌟 Philosophy
We believe in **"Small models, Great tools."** 
- **Privacy First**: Everything should run locally by default.
- **Surgical Precision**: We prefer high-precision tools (Grep, MCP) over high-token hallucinations.
- **Studio Aesthetic**: The UI must remain clean, immersive, and premium.

---

## 🛠️ How Can I Contribute?

### 1. Adding a New Worker (Agent)
If you want to add a specialized worker (e.g., a `Tester`, a `Security Expert`, or a `SQL Expert`):
- Add a new state in `app/agents/state.py`.
- Create a new skill in `app/agents/skills/`.
- Update the router in `app/agents/nodes/router.py` to handle the new delegation.

### 2. Enhancing the MCP Ecosystem
Vibrisse is **MCP-Native**. You can contribute by:
- Testing and documenting new MCP servers from the community.
- Adding pre-configured server definitions in the UI.
- Improving the `app/services/mcp/mcp_client.py` for better stability.

### 3. Improving Surgical RAG
Help us make retrieval even better:
- Optimize the `app/services/rag/` layer.
- Improve the Ripgrep integration in `app/agents/nodes/retrieval.py`.
- Add support for new file types or documentation formats.

### 4. Polishing the "Obsidian Glass" UI
- Help us split the large CSS files into modular components.
- Add micro-animations (GSAP/Framer Motion).
- Improve the `ThinkingConsole` visualization.

---

## 🚀 Technical Setup for Developers

1. **Clone & Install**:
   ```bash
   git clone https://github.com/QuentinMerle/vibrisse-agent.git
   cd vibrisse-agent
   python3.12 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Frontend Development**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Backend Development**:
   ```bash
   # Run with hot-reload
   uvicorn app.main:app --reload --port 8001
   ```

---

## 📜 Pull Request Guidelines
- **Focus**: One feature per PR.
- **Quality**: Ensure your code follows the existing DDD structure.
- **Testing**: If you add a tool, add a test case in `docs/TEST_SCENARIOS.md`.
- **Aesthetics**: If you modify the UI, ensure it respects the "Obsidian Glass" variables.

---

## 💬 Community & Support
- **Discord**: [Join our community](https://discord.gg/vibrisse) (Placeholder)
- **Twitter**: [@VibrisseAI](https://twitter.com/vibrisseai) (Placeholder)

Thank you for helping us build the future of local AI! 🐱🚀
