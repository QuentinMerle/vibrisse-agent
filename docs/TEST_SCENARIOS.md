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
- [ ] **GitHub Alerts**: Verify that Markdown blockquotes styled as alerts (e.g. `> [!WARNING]`) are rendered with the correct border color and icon in the `MessageBubble`.

---

## 🏛️ Planning Mode & Artifacts (Antigravity Experience)

### 14. Planning Mode (Human-in-the-Loop)
*   **Goal**: Verify that complex tasks trigger the architect planning mode and pause execution.
*   **Prompt**: "Je souhaite refondre complètement la navigation du site pour ajouter React Router, migrer le composant Header.jsx vers cette nouvelle navigation, et configurer des transitions de pages avec GSAP entre la MainStudio.jsx et une nouvelle page. Propose-moi un plan détaillé pour cette refonte."
*   **Expected**:
    1. The agent detects a complex structural task affecting multiple files (`src/App.jsx`, `Header.jsx`, etc.).
    2. It switches to the Architect persona and generates a detailed Markdown plan wrapped in `<artifact id="plan">` tags.
    3. The thinking console stops and the UI displays an approval block waiting for your decision.

### 15. Interactive Artifact View
*   **Goal**: Verify that `<artifact>` tags are intercepted and rendered as a dedicated UI component.
*   **Prompt**: "Génère-moi une proposition de composant React Three Fiber pour un fond interactif en particules pour le site. Mets le code de ce composant dans un artefact nommé r3f-particle-bg."
*   **Expected**: 
    1. The agent drafts the 3D component using R3F.
    2. The raw text of its response only shows explanations.
    3. The R3F component code is extracted from the XML and displayed in the chat interface as a clean "Artefact: r3f-particle-bg" block, without raw `<artifact>` tags.

### 16. Plan Execution Resumption
*   **Goal**: Verify that user action on the approval widget properly resumes the agent's workflow.
*   **Action**: Trigger the planner using the prompt from Point 14. Once the plan is rendered with the approval block below:
    - **Test Approve**: Click "Approuver le plan". The agent starts writing files or installing packages.
    - **Test Reject**: Click "Rejeter". The agent receives the rejection event, aborts the modification, and asks for clarification to formulate a new proposal.
*   **Expected**:
    1. The frontend calls the `/api/chat/approve` endpoint with `approved=true` or `approved=false`.
    2. The `PlanApproval` inline block disappears.
    3. The agent streams the continuation of its task (writing code) or asks for clarification.

### 17. CodeDiff Artifact (Preview Changes)
*   **Goal**: Verify that the agent can generate a visual code difference preview before executing a `write_file` operation.
*   **Prompt**: "Je veux ajouter un effet 'glassmorphism' supplémentaire sur le composant `PlanModal.css`. Fais-moi une proposition de modification et affiche-la sous forme de diff dans un artefact nommé `glass-diff` avant d'appliquer."
*   **Expected**:
    1. The agent responds with a `<artifact id="glass-diff">` containing a code block with the `diff` language.
    2. The `ArtifactView` component renders the diff clearly showing the `+` additions and `-` removals for the CSS.
    3. The agent awaits confirmation before using its writing tools.

### 18. Architecture Artifact (Mermaid Diagrams)
*   **Goal**: Verify that the agent can generate interactive architectural diagrams for the Vibrisse system.
*   **Prompt**: "Génère un diagramme Mermaid illustrant le flux complet d'un message utilisateur : depuis la saisie dans `ChatInput.jsx`, le passage par le `stream_service.py` et le routeur LangGraph, jusqu'au rendu final dans `MessageBubble.jsx`. Mets-le dans un artefact nommé `arch-flow`."
*   **Expected**:
    1. The agent traces the logic across the frontend and backend.
    2. It responds with an `<artifact id="arch-flow">` containing a `mermaid` code block.
    3. The `ArtifactView` correctly interprets and renders the interactive visual diagram instead of raw markdown text.

### 19. TaskBoard Artifact (Living Checklist)
*   **Goal**: Verify that the agent can manage and visually update long-running multi-file tasks using a checklist artifact.
*   **Prompt**: "Crée un TaskBoard dans un artefact nommé `i18n-taskboard` pour implémenter l'internationalisation de la modale des paramètres. Les étapes sont : 1. Créer `fr.json`, 2. Mettre à jour `SettingsModal.jsx`, 3. Ajouter le sélecteur de langue."
*   **Expected**:
    1. The agent generates a `<artifact id="i18n-taskboard">` containing a Markdown task list (`- [ ]`).
    2. As the agent progresses through steps, it updates the artifact in subsequent messages.
    3. The UI reflects the checked items (`- [x]`) showing real-time progress for long-running goals.