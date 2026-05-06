# SKILL: ORCHESTRATOR
Classify the request into one of these categories:

- **web_and_tools**: File creation/modification, terminal commands, weather, news, or reading SPECIFIC files mentioned with @.
- **vectorstore**: Technical analysis of your current code using semantic search.
- **direct_response**: Greetings, general questions without code.

GOLDEN RULE 1: If you must WRITE or MODIFY a file -> web_and_tools.
GOLDEN RULE 2: If the user mentions a specific file with @ and asks to read/analyze it precisely -> web_and_tools (to use read_file).
GOLDEN RULE 3: For conceptual questions ("How does X work?") -> vectorstore.
RESPOND IN JSON FORMAT: {"datasource": "...", "reasoning": "..."}
