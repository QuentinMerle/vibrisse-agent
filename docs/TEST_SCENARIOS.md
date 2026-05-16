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

## 👻 Advanced Agentic Features

### 6. Ghost Mode (In-File Directives)
*   **Goal**: Verify that the agent can read and execute instructions hidden in comments.
*   **Prompt**: "Process the Ghost Mode instructions in `app/agents/nodes/router.py`."
*   **Expected**: The agent reads the file, finds comments starting with `VIBRISSE:`, and performs the requested task.

### 7. Sovereign Routing (Offloading)
*   **Goal**: Verify the "Cloud-to-Local Savings" logic.
*   **Prompt**: "I want to perform a heavy analysis. Should we offload to Claude or stay on oMLX?"
*   **Expected**: 
    1.  The agent analyzes the task complexity.
    2.  It proposes a "Sovereign Proposal" (UI modal).
    3.  Choose your path and verify the switch.

### 8. Thought Graph Observability
*   **Goal**: Ensure the visual workflow is accurate.
*   **Prompt**: "Research the latest news about SpaceX and then write a summary in a new file `spacex.md`."
*   **Expected**: 
    1.  **Graph**: See `Supervisor` -> `Coder` -> `Web_search`.
    2.  **Graph**: See `Coder` -> `Write_file`.
    3.  Verify the nodes are spread correctly (no overlap).

### 9. Persistent MCP Hub
*   **Goal**: Verify connection to external MCP servers.
*   **Prompt**: "Use the connected MCP server to [action specific to your server]."
*   **Expected**: The agent lists the MCP tools in its planning and executes them via the `mcp_client`.

---

## 🌐 Research & Vision

### 10. `web_search` (Real-time)
*   **Goal**: Verify external data access.
*   **Prompt**: "What is the latest stable version of LangGraph? Search the web."
*   **Expected**: The agent calls `web_search`, cites its sources, and provides the version.

### 11. Vision Analysis
*   **Goal**: Verify image understanding.
*   **Prompt**: (Attach a screenshot of a UI component) "Describe this UI and suggest improvements."
*   **Expected**: The agent uses its vision capability to describe colors, layout, and components.

---

## 🧠 Core Intelligence

### 12. Router Calibration
*   **Goal**: Ensure intent is directed to the right node.
*   **Tests**:
    -   "Hello!" -> Should go to `direct_response`.
    -   "How does the backend work?" -> Should go to `vectorstore` (RAG).
    -   "What's the weather in Paris?" -> Should go to `web_and_tools`.

### 13. Expert Review
*   **Goal**: Verify that large models (Claude/GPT) perform a quality check on small model outputs.
*   **Prompt**: (Ask a complex coding question using a large model)
*   **Expected**: See the `expert_review_node` in the ThinkingConsole and the improved final code.

---

## 🎨 UI/UX Validation
- [ ] **Auto-scroll**: The ThinkingConsole should follow the stream automatically.
- [ ] **Settings Persistence**: Change the model and refresh; it should stay.
- [ ] **Responsive Modals**: Verify that Settings and Approvals are scrollable on small screens.
- [ ] **Theme Consistency**: Verify the "Obsidian Glass" consistency across all components.
- [ ] **Graph Spacing**: Confirm no node overlap (Supervisor, Workers, Tools).
