## 🍎 macOS & Environment Strategy

Vibrisse Agent is primarily developed and validated on **macOS** with **Python 3.12**.

### 🛠️ The "Safety-First" Installation Pattern
On macOS, especially with Python 3.12, some packages (like `unstructured` or `whisper`) may fail during build if tools like `setuptools` or `wheel` are missing in the virtual environment.

**Always follow this initialization pattern:**
```bash
# 1. Create the venv
python3.12 -m venv .venv

# 2. Upgrade core tools first (Crucial for Python 3.12)
./.venv/bin/python -m pip install --upgrade pip setuptools wheel

# 3. Install dependencies from the validated stack
./.venv/bin/python -m pip install -r requirements.txt
```

### 🐍 Python Path Best Practices
Avoid using global `pip` or `python` commands. Always target the local environment explicitly to ensure persistence and isolation:
- **Good**: `./.venv/bin/python -m pip install ...`
- **Avoid**: `pip install ...` (might target system Python or a different version)

### ⚠️ Version Sensitivity (The LangGraph Trap)
**DO NOT** update `langchain` or `langgraph` beyond the versions specified in `requirements.txt` without rigorous testing.
- **Why?** Upgrading from `langchain 0.3.x` to `1.0.x` or `langgraph 0.6.x` to `1.x` introduces breaking changes in serialization and tool result formats.
- **Symptoms**: Deserialization errors in `AsyncSqliteSaver`, empty message history on reload, or `ImportError: ModelProfile`.

### 🧹 Environment Recovery
If the environment becomes unstable (e.g., after a failed package update):
1. Delete the virtual environment: `rm -rf .venv`
2. Reset the persistence database (optional but recommended if serialisation fails): `rm data/checkpoints.db`
3. Re-initialize using the "Safety-First" pattern above.
