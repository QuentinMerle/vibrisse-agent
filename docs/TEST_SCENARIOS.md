# 🧪 Vibrisse Agent - Test Scenarios & Tool Validation

This document outlines the standard test scenarios for validating Vibrisse Agent's tools and capabilities. Use these prompts and steps to ensure everything is functioning correctly after an update.

## 📁 Filesystem & Exploration Tools

### 1. `list_dir` (Explorer)
*   **Goal**: Verify that the agent can see the project structure.
*   **Prompt**: "List the files in the root directory of this project."
*   **Expected**: The agent calls `list_dir('.')` and displays the main folders/files (`app/`, `frontend/`, `README.md`, etc.).

### 2. `read_file` (Surgical Reading)
*   **Goal**: Verify the agent can read specific content.
*   **Prompt**: "Read the content of `frontend/src/App.jsx` and explain the main components used."
*   **Expected**: The agent calls `read_file('frontend/src/App.jsx')` and provides a summary.

### 3. `grep_search` (Search)
*   **Goal**: Verify exact term matching.
*   **Prompt**: "Search for where the 'ThinkingConsole' component is used in the frontend."
*   **Expected**: The agent calls `grep_search('ThinkingConsole', search_path='frontend')` and identifies the relevant files.

---

## 🛠️ Maker & System Tools

### 4. `write_file` (Maker Mode)
*   **Goal**: Verify file creation/update.
*   **Prompt**: "Create a new file called `TEST_DUMMY.md` in the root with the text 'Vibrisse Test Passed'."
*   **Expected**: The agent calls `write_file` and reports success. Check the local filesystem to confirm.

### 5. `run_terminal_command` (Security & HITL)
*   **Goal**: Verify command execution and Human-in-the-Loop validation.
*   **Prompt**: "Check the current node version in the terminal."
*   **Expected**: 
    1.  Agent calls `run_terminal_command('node -v')`.
    2.  **UI Action**: A security modal appears asking for authorization.
    3.  **Validation**: Click "Authorize".
    4.  **Result**: The agent displays the version.

---

## 🌐 Research & Vision

### 6. `web_search` (Real-time)
*   **Goal**: Verify external data access.
*   **Prompt**: "What is the latest stable version of LangGraph? Search the web."
*   **Expected**: The agent calls `web_search`, cites its sources, and provides the version.

### 7. Vision Analysis
*   **Goal**: Verify image understanding.
*   **Prompt**: (Attach a screenshot of a UI component) "Describe this UI and suggest improvements."
*   **Expected**: The agent uses its vision capability to describe colors, layout, and components.

---

## 🧠 Core Intelligence

### 8. Router Calibration
*   **Goal**: Ensure intent is directed to the right node.
*   **Tests**:
    -   "Hello!" -> Should go to `direct_response`.
    -   "How does the backend work?" -> Should go to `vectorstore` (RAG).
    -   "What's the weather in Paris?" -> Should go to `web_and_tools`.

### 9. Expert Review
*   **Goal**: Verify technical optimization.
*   **Prompt**: "Write a complex React hook for managing a websocket connection with auto-reconnect."
*   **Expected**: After the initial draft, the `expert_review` node should trigger (visible in `ThinkingConsole`) to refine the code.

---

## 🌍 Internationalization (i18n)

### 10. Language Switch
*   **Goal**: Verify UI bilinguality.
*   **Steps**:
    1.  Go to **Settings > General**.
    2.  Switch to **English**. Verify UI labels change.
    3.  Switch to **French**. Verify UI labels change.
    4.  Start a new chat. Verify the initial message matches the chosen language.

---

## 📊 System Monitoring

### 11. System Pulse
*   **Goal**: Verify metrics accuracy.
*   **Steps**: Observe the Sidebar Cockpit. (V)RAM and Context usage should reflect current activity. Tooltips should show detailed bytes/limits.
