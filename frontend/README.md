# 🎨 Vibrisse Agent UI

L'interface de contrôle "Obsidian Glass" de Vibrisse Agent. Une Single Page Application (SPA) haute performance construite avec **React** et **Vite**.

## 🚀 Stack Technologique

- **Framework** : React 18
- **Build Tool** : Vite
- **Styling** : Vanilla CSS (Zéro framework CSS pour un contrôle total sur les performances et l'esthétique)
- **State Management** : Zustand (Léger et performant)
- **Communication** : SSE (Server-Sent Events) pour le streaming en temps réel des tokens et des pensées.

---

## 🛠️ Développement

```bash
# Installation des dépendances
npm install

# Lancement en mode développement (Port 5173 par défaut)
npm run dev

# Build pour la production
npm run build
```

> **Note** : En développement, l'interface s'attend à trouver le backend sur `http://localhost:8001`. Vous pouvez modifier cela dans `src/services/api.js`.

---

## 📂 Structure du Projet

- `src/components/` : Composants UI atomiques et modulaires.
- `src/hooks/` : Logique métier déportée (ex: `useChatStream.js` pour la gestion complexe du SSE).
- `src/services/` : Clients API et configurations de communication.
- `src/utils/` : Helpers de formatage (Markdown, dates, calculs).
- `public/fonts/` : Polices de caractères auto-hébergées pour garantir le rendu offline.

---

## 🎨 Design System

L'interface suit strictement les directives de **`DESIGN.md`** (à la racine du projet).
- Toutes les couleurs sont des variables CSS définies dans `src/index.css`.
- Nous n'utilisons pas de bibliothèques de composants externes (comme MUI ou Tailwind) pour préserver l'identité visuelle unique "Obsidian Glass".

---

## 🧠 Concepts Clés

### Streaming SSE & Pensées
L'interface ne reçoit pas juste du texte, elle gère un flux d'événements typés. Le hook `useChatStream` est le cœur du système : il accumule les `thoughts` (pensées) dans la `ThinkingConsole` tout en streamant le `final_content` dans la bulle de message.

### Performance
L'usage de Vanilla CSS et l'absence de grosses dépendances permettent d'atteindre un score Lighthouse quasi parfait, assurant une réactivité instantanée même sur de longs historiques de chat.
