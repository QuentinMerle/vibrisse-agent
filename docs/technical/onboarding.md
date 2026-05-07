# 🚀 Technical Documentation: Smart Onboarding Wizard

Vibrisse uses a "Resource-Aware" onboarding process to ensure that even users with limited hardware can get professional performance from local models.

## 🏗️ Architecture Overview

The onboarding flow is a bridge between the user's physical hardware and the agent's persona strategy.

### 1. Discovery Phase (`SystemDiscoveryService`)
- **Memory Tracking**: Uses `psutil` to detect Total vs Available RAM.
- **GPU Acceleration**: Detects Apple Silicon (M1/M2/M3) or NVIDIA GPUs (via `torch` or `nvidia-smi`).
- **Tiering Logic**: Classifies the machine into three tiers:
    - **LOW**: < 12GB total memory (Optimized for 2B-3B models).
    - **MID**: 12GB - 48GB memory (Optimized for 7B-9B models).
    - **HIGH**: > 48GB memory (Optimized for 27B-70B models).

### 2. Persona Strategy
Vibrisse recommends specific models based on the detected tier and the user's professional profile:

| Persona | LOW Tier | MID Tier | HIGH Tier |
| :--- | :--- | :--- | :--- |
| **Generalist** | Phi-3 Mini | Llama-3 8B | Llama-3 70B |
| **Expert Coder** | CodeLlama 7B | Codestral | DeepSeek Coder V2 |
| **Data Scientist** | Gemma-2 2B | Gemma-2 9B | Gemma-2 27B |
| **Tech Writer** | Phi-3 Mini | Mistral Nemo | Command-R |
| **Architect** | Mistral 7B | Command-R | Command-R+ |

### 3. Persistence & State Management
- **Backend-Driven**: The source of truth for the "Onboarded" status is stored in `data/session.json`.
- **API Endpoint**: `/api/system/config` returns the `onboarded` boolean.
- **Wizard Trigger**: The frontend checks the backend flag on every launch to ensure a consistent experience across browsers.

## 🛠️ Key Components

- **Frontend**: `OnboardingWizard.jsx` (Navigation & Steps), `PersonaCard.jsx` (Modular UI).
- **Backend**: `system.py` (API Endpoints), `system_discovery.py` (Hardware Logic), `session_service.py` (Persistence).

---
*Vibrisse AI: Small models, Great tools.*
