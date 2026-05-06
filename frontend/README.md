# 🎨 Vibrisse Agent UI — "Obsidian Glass"

The "Obsidian Glass" control interface for Vibrisse Agent. A high-performance Single Page Application (SPA) built with **React** and **Vite**, designed to provide a premium, studio-grade experience for local AI engineering.

## 🚀 Technical Stack

-   **Framework**: React 18 (Functional Components & Hooks)
-   **Build Tool**: Vite (Lightning-fast HMR and optimized production builds)
-   **Styling**: Vanilla CSS (Zero CSS frameworks used to ensure total control over performance, aesthetics, and theme tokens)
-   **Internationalization**: `react-i18next` (Full multi-language support: EN/FR)
-   **Communication**: SSE (Server-Sent Events) for real-time streaming of tokens, thoughts, and system status.
-   **Icons**: Lucide React

---

## 🎭 Design Philosophy

Vibrisse follows the **Obsidian Glass** design system:
-   **Immersive Dark Mode**: Deep blacks (`#09090b`) and smoked glass surfaces.
-   **Visual Feedback**: Real-time monitoring of (V)RAM, Context usage, and System health.
-   **Expert Mode**: A dedicated `ThinkingConsole` with terminal aesthetics to visualize the agent's internal reasoning.
-   **Fluidity**: Micro-animations, skeleton loaders, and hardware-accelerated transitions.

---

## 🛠️ Development & Build

```bash
# Install dependencies
npm install

# Launch development mode (Default: http://localhost:5173)
npm run dev

# Build for production (Optimized chunks)
npm run build
```

> **Note**: In dev mode, the UI expects the backend API at `http://localhost:8001`. This can be configured in `src/services/api.js`.

---

## 📂 Project Architecture

-   `src/components/`: Atomic and modular UI components (Chat, Layout, Cockpit).
-   `src/hooks/`: Business logic decoupled from UI (e.g., `useChatStream.js` for complex SSE management).
-   `src/i18n/`: Translation configuration and locale JSON files.
-   `src/services/`: API clients and streaming services.
-   `src/index.css`: Global design system tokens and typography resets.

---

## ⌨️ Productivity Features

-   **Keyboard Shortcuts**:
    -   `CMD/CTRL + K`: Focus input bar instantly.
    -   `CMD/CTRL + B`: Toggle Sidebar (Slim/Expanded mode).
    -   `CMD/CTRL + N`: Start a new clean discussion.
-   **Smart Mentions**: Type `@` in the input bar to cite and attach local files to the context.
-   **Voice Control**: Integrated speech-to-text recognition (Web Speech API).

---

## ♿ Accessibility & UX

Vibrisse is built with inclusivity and professional ergonomics in mind:
-   **Semantic HTML**: Proper use of sectioning elements and ARIA roles.
-   **Keyboard Navigation**: All interactive elements are reachable and operable via keyboard.
-   **Internationalization**: Native support for multiple languages with instant switching.
-   **Responsive Design**: A fluid layout that adapts to different screen sizes while maintaining the "Cockpit" feel.

---

## 🧠 Key Concepts

### Event-Driven Streaming
Vibrisse doesn't just receive text; it processes a stream of typed events. The `useChatStream` hook is the core of the system: it separates `thoughts` (reasoning) into the `ThinkingConsole` and `chunks` (content) into the message bubbles.

### Optimized Chunking
The production build uses advanced Rollup chunking to separate vendor libraries (`react`, `react-markdown`, `lucide`) from application logic, ensuring fast initial load times and efficient browser caching.

---

*Vibrisse UI: Where engineering precision meets state-of-the-art aesthetics.*
