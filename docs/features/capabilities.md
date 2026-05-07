# 🛠️ Agent Capabilities (Tools)

Vibrisse is an action-oriented agent. Beyond simple chat, it can interact with your system through a set of specialized tools.

## 📂 System Exploration
- **`list_dir`**: Lists files and directories to understand the project structure.
- **`read_file`**: Reads the content of a specific file for surgical analysis.
- **`grep_search`**: High-speed exact term matching using `ripgrep`.

## ✍️ Maker Mode (File Manipulation)
- **`write_file`**: Creates or updates files (documentation, code, configuration). *Requires human approval.*

## 💻 System Power
- **`run_terminal_command`**: Executes any shell command. Used for running tests, installing dependencies, or checking system state. *Strictly requires human approval.*

## 👁️ Vision Analysis
- Native capacity to analyze images (screenshots, UI mocks, architecture diagrams) via multimodal models.

## 🛡️ Expert Review
- Every complex technical answer is automatically reviewed by a specialized "Reviewer" agent to ensure quality and technical fidelity.

## 🌐 Web Access
- **`web_search`**: Accesses real-time data via Tavily or DuckDuckGo (Weather, latest tech documentation, news).

---
*Vibrisse AI: Small models, Great tools.*
