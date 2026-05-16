# 🚀 Inference Engines Guide: Which one to choose?

Vibrisse is a **Sovereign Universal Agent**. Thanks to its support for the OpenAI API standard, you can connect it to various inference backends depending on your needs.

## 📊 Comparison Table

| Engine | Best For | Key Advantage | Default Port |
| :--- | :--- | :--- | :--- |
| **Ollama** | Solo Dev / Desktop | Easiest to setup, handles model management. | `11434` |
| **oMLX** | Mac Power User | **Optimized for Apple Silicon**. SSD KV-Cache persistence. | `8080` |
| **vLLM** | Enterprise / Server | High throughput, PagedAttention, Multi-GPU. | `8000` |
| **TGI (Hugging Face)** | Production / RAG | Very stable, optimized for high-demand apps. | `8080` |
| **LocalAI** | All-in-one | Supports Vision, Audio, and Image generation. | `8080` |
| **LM Studio / Jan** | GUI Enthusiasts | Great for manually loading and testing `.gguf` files. | `1234` |
| **LiteLLM (Proxy)** | Governance | Unifies 100+ providers under a single OpenAI endpoint. | `4000` |

---

## 🛠️ How to connect them to Vibrisse

### 1. Ollama (Native)
Use the **"Ollama (Local)"** provider in Settings.
- **Endpoint**: `http://localhost:11434` (Automatic)

### 2. oMLX / vLLM / LM Studio / LocalAI (Custom OpenAI-Compatible)
Use the **"Custom"** provider in Settings.
- **URL**: Saisissez l'URL complète incluant `/v1`.
    - **oMLX default**: `http://localhost:8080/v1`
    - **vLLM default**: `http://localhost:8000/v1`
- **Model**: Enter the exact model ID exposed by your server (e.g., `llama-3.1-8b-instruct`).

### 🍏 Special Note for Mac Users: Why oMLX?
If you are on an Apple Silicon Mac, **oMLX** is highly recommended for coding tasks. 
- **Context Persistence**: It saves the "brain state" of the agent on your SSD. If you ask a follow-up question later, the agent doesn't need to re-read your whole project—it's ready in milliseconds.
- **Unified Memory**: It's built on Apple's MLX framework, making it more efficient than general-purpose engines.

### 3. LiteLLM (The "Enterprise" Choice)
If you work in a team, we recommend using **LiteLLM** as a gateway.
- You can route requests between local models (vLLM) and cloud models (Groq/OpenRouter) transparently.
- Vibrisse will only see one "Custom" endpoint, while LiteLLM handles the complexity behind the scenes.

---
*Vibrisse AI: Small models, Great tools.*
