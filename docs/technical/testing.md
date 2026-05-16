# 🧪 Testing Strategy & Quality Assurance

Vibrisse Agent uses a tiered testing strategy to ensure reliability for both end-users and contributors.

## 1. Sanity Check (User-Facing)
**Script**: `scripts/sanity_check.py`

This is the first line of defense for users. It verifies the local environment without running the full test suite.
- **Python Version**: Ensures 3.12+ is used.
- **Ollama**: Checks if the Ollama server is reachable on port 11434.
- **Ripgrep**: Verifies if `rg` is available for surgical RAG operations.
- **Permissions**: Confirms that the `~/.vibrisse` directory is writable.

## 2. Unit & Integration Tests (Contributor-Facing)
**Framework**: `pytest`
**Location**: `tests/unit/`

These tests validate the core logic of the agent's "bricks".
- **Ghost Mode Detection**: Validates the regex and scanner logic in `GhostService`. Ensures that directives like `@vibrisse:` are correctly extracted from source code.
- **MCP Persistence**: Validates the SQLite storage for Model Context Protocol servers. Tests the full cycle: *Save -> Load -> Disconnect*.

**Run command**:
```bash
pytest tests/unit/
```

## 3. Manual Validation Scenarios
**Document**: `docs/TEST_SCENARIOS.md`

High-level scenarios to verify the "feel" and complex tool interactions (e.g., UI modals, streaming). These are used before a release to ensure the Studio experience is fluid.

## 4. Future: Automated Evaluation (RAGAS)
**Status**: Planned

We aim to implement a specialized evaluation suite using the **RAGAS** framework to score:
- **Faithfulness**: Does the agent use the retrieved code accurately?
- **Relevancy**: Does the answer solve the user's specific problem?
- **Safety**: Does the agent properly ask for permission before sensitive tool calls?

---
*Vibrisse AI: Small models, Great tools.*
