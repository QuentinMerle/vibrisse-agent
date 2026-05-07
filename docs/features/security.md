# 🛡️ Security & Privacy

Vibrisse is built with a **Security-by-Design** approach to protect your code and data.

## 🏠 Local-First & Sovereignty
If using **Ollama**, no line of your code or conversation leaves your machine. Vibrisse works perfectly offline and ensures complete data sovereignty.

## 🤝 Human-in-the-Loop (HITL)
The agent is strictly forbidden from executing system commands (`run_terminal_command`) or writing files (`write_file`) without your explicit validation in the UI. You are always the final decision-maker.

## 🧼 Secret Scrubbing
An automatic filtering system masks API keys, tokens, and passwords that might accidentally appear in agent logs or thought processes.

## 📂 Data Isolation
- Your chat history and vector indices are stored locally in the `/data` folder.
- This folder is strictly excluded from Git tracking to prevent accidental leaks.

## 🛡️ Safety Ingestion Shield
To protect your machine during indexing:
- **Batch Processing**: Files are indexed in groups of 50 to keep RAM usage stable.
- **Size Filtering**: Files larger than 1MB are automatically ignored.
- **Intelligent Exclusions**: Common heavy folders (`node_modules`, `.next`, `dist`, etc.) are ignored by default.

---
*Vibrisse AI: Small models, Great tools.*
