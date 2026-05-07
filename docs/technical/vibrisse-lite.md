# 🕊️ Vibrisse Lite - Strategic Concept & Technical Roadmap

This document serves as the technical manifesto and implementation plan for **Vibrisse Lite**, a version of the agent specifically engineered for low-resource environments and small-scale local models (7B/8B).

> [!IMPORTANT]
> **Status**: Vibrisse Lite is planned as a **separate, standalone version** (potentially written in Rust) to be developed after the public release of the main Vibrisse Agent (Studio).

---

## 🧠 Vision: "The Surgical Edge"
Vibrisse Lite follows the principle that **efficiency is a form of intelligence**. Instead of relying on brute-force context windows and massive vector stores, Lite uses high-precision tools and a streamlined architecture to provide a professional experience on consumer-grade hardware.

---

## 🏗️ Technical Pillars (Deep Dive)

### 1. The Nano-Kernel Architecture (Linear Dispatcher)
The main bottleneck in agentic systems is the "Reasoning Loop" (thinking about what to do).
- **Current State**: Cyclic graph with complex state management (LangGraph).
- **Lite Strategy**: **Deterministic Routing**.
    - **Step A**: A micro-classifier (Regex-based or a 100M parameter model like `SmolLM-135M`) analyzes the user intent.
    - **Step B**: The system selects one of 3 hardcoded "Fast-Paths": `QUICK_CODE`, `DOC_SEARCH`, or `DIRECT_CHAT`.
    - **Optimization**: We bypass the LangGraph state reducer overhead for simple queries.

### 2. Hybrid "Skeleton & Grep" RAG
Traditional RAG is too heavy for 8GB RAM machines (Vector DB + Embedding Model).
- **Phase 1: Skeleton Indexing**: 
    - At startup, we scan the project to extract *only* the signatures (e.g., `def my_function(param):`).
    - We store these signatures in a simple **Prefix Tree (Trie)** or a tiny **USearch** index.
- **Phase 2: JIT (Just-In-Time) Grep**: 
    - When the agent needs details about a class, it triggers a `ripgrep` search on the keyword.
    - `rg` is written in Rust and can scan 100k lines in milliseconds. It replaces the need for "Dense Vector Search" for most coding tasks.

### 3. Tooling: XML & Dynamic Pruning
Small models often hallucinate JSON syntax or forget tool parameters.
- **XML-Based Protocol**: We shift from JSON tool calls to XML tags (e.g., `<call:read_file path="..."/>`). 
    - *Reasoning*: LLMs are natively better at closing tags than balancing braces in JSON.
- **Skill-on-Demand**: Instead of a system prompt containing all 15 capabilities, the agent is only "aware" of 2-3 tools at a time based on the active route.

### 4. Native Performance (The "Sidecar" Runner)
Bypass the overhead of multiple HTTP layers.
- **Direct Bindings**: Use `llama-cpp-python` or `mlx-lm` directly in the process instead of communicating with a separate Ollama server.
- **Aggressive Quantization**: Native support for **K-Quants (Q4_K_M)** or **IQ4_XS** which provide the best performance/intelligence ratio for 8B models.
- **Prompt Compression**: Implementation of a **Windowed Summary Cache**. We don't send the last 20 messages, but a "Compressed Summary" + the last 2 messages.

---

## 🗺️ Technical Roadmap (Implementation Phases)

### Phase 1: The "Slim-Fast" Foundation
- [ ] **Dependency Audit**: Create a `requirements-lite.txt` excluding heavy libs (ChromaDB, full LangChain).
- [ ] **Native Integration**: Implement a `LiteRunner` class that abstracts `llama.cpp` / `MLX`.
- [ ] **Stateless Session**: Switch conversation persistence from SQLite to a simple atomic JSON append-only log.

### Phase 2: The Surgical RAG Engine
- [ ] **Project Skeletonizer**: A script that generates a `.vibrisse-map` (JSONL) containing only signatures.
- [ ] **Grep-Integration**: Build a Python wrapper around `rg` (ripgrep) that returns context-aware snippets (line N +/- 5 lines).
- [ ] **Hybrid Router**: Logic to decide when to use the Skeleton Index vs. raw Grep.

### Phase 3: Intelligence Adaptation
- [ ] **XML Parser**: Robust regex-based parser for XML tool calls.
- [ ] **Prompt Pruner**: A middleware that strips "fluff" from system instructions based on the current hardware profile (detected at startup).
- [ ] **Atomic Tasks**: Modify the orchestrator to force the model to solve complex problems in 3 atomic steps max.

### Phase 4: UI & UX Optimization
- [ ] **Studio Lite**: A dedicated CSS theme that removes blurs and heavy animations (GPU-friendly).
- [ ] **Instant-TUI**: Optimize the Terminal UI for low-latency feedback.

---

## 🛡️ Security & Privacy in Lite
- **Memory-Only Cache**: Ability to run in "Incognito Mode" where no data touches the disk.
- **Local-Only Lock**: Hard-coded restriction to `127.0.0.1` at the kernel level.
- **Sandbox-Lite**: Use `os.chroot` or simple path validation to ensure the agent never leaves the `TARGET_PROJECT_PATH`.

---

## 🎨 UX & Persona Orchestration (The Lite Experience)

Efficiency is nothing without relevance. Vibrisse Lite uses a "Zero-Friction" onboarding and a layered prompting system to adapt to the user's profile without overloading the model.

### 1. Resource-Aware Onboarding
At startup, the Lite binary performs a silent **Hardware Check** (RAM, CPU, GPU) and suggests a profile:
- **Low-End (8GB RAM)**: Recommends **Phi-3 (3B)** or **Llama-3 (8B) Q4**.
- **Mid-Range (16GB RAM)**: Recommends **Mistral-7B v0.3** or **Gemma-2-9B**.

### 2. Layered Prompting System
To maximize the "Intelligence Density" of small models, we replace monolithic system prompts with a **Three-Layer Stack**:
1. **Base Layer (Identity)**: Core rules, safety, and XML/Grammar formatting instructions.
2. **Persona Layer (Expertise)**: 5-10 lines of high-impact instructions tailored to the user.
    - *Student Coder*: Mentor mode, focus on "Why" and "How", not just the code.
    - *Law Student*: Strict source citations, focus on logical structure and semantic ambiguity.
3. **Context Layer (JIT)**: Surgical injection of relevant file metadata via the Skeleton Index.

### 3. Persona Profiles (Lite Matrix)

| Persona | UX Focus | Recommended Model (Lite) |
| :--- | :--- | :--- |
| **Student Coder** | Step-by-step explanations, interactive debugging. | **Llama-3-Coder (8B)** |
| **Law Student** | Document comparison, terminology extraction. | **Mistral-7B-Instruct** |
| **Creative Writer**| Outlining, stylistic corrections. | **Gemma-2-9B** |

### 4. The "Prompt Mixer" Middleware
A lightweight logic layer that "assembles" the prompt in real-time. It uses **Token Pruning** to remove filler words and fluff from instructions, ensuring the model's limited context window is dedicated to the actual problem solving.

---

## 🧘 Vibrisse Zen: The "Pure" Path (Architectural Challenge)

For the ultimate version of Lite, we challenge the "App/Server" paradigm and look for the most minimalist, high-performance way to bridge a small model with a local codebase.

### 1. The Single-Binary Kernel (Rust)
- **Challenge**: Python and HTTP APIs introduce significant memory and latency overhead.
- **Zen Path**: A single binary written in **Rust** using **Candle** or static **llama.cpp** bindings.
    - No Python runtime required.
    - RAM usage: ~20MB (engine) + Model weights.
    - Zero-latency IPC (Inter-Process Communication) instead of HTTP.

### 2. Holographic Context (AST-Driven)
- **Challenge**: RAG "chunks" lose the structural meaning of code.
- **Zen Path**: Instead of vectors, use a **Global Abstract Syntax Tree (AST)**.
    - The agent navigates a **Logical Map** of the project, not a list of snippets.
    - The "Index" is a compressed representation of code topology always present in the latent space of the model.

### 3. Intelligence by Constraint (GBNF Grammars)
- **Challenge**: Natural language reasoning (Chain of Thought) is slow and verbose.
- **Zen Path**: Use **GBNF (Grammar-Based Native Functions)**.
    - Force the model to output directly into a binary or highly-compressed structural protocol.
    - Eliminate the "Thought" steps in natural language to focus 100% of the compute on the **Logic of Action**.

### 4. The Transparent Daemon
- **Challenge**: Switching to a separate Chat UI breaks developer flow.
- **Zen Path**: Vibrisse as a **Headless Daemon**.
    - No "Chatbot" personality. It acts as a surgical extension of the text editor/shell.
    - Intelligence is injected via "Ghost Text" or direct file mutation, behaving like a smart operating system component rather than a conversational partner.

---
*Drafted by the Vibrisse Lead Tech Strategy Group - Zen Revision (Planned as a standalone version after the public release of Vibrisse Agent).*
