# 🎨 Vibrisse Design System — "Obsidian Glass"

Ce fichier est la **source de vérité visuelle** du projet. Il doit être lu par tout agent IA avant de créer ou modifier un composant UI.

> **Règle d'or** : Ne jamais inventer une couleur, un espacement ou une police à la volée. Tout doit être tiré des tokens définis ici. En cas de doute, consulter `frontend/src/index.css`.

---

## 🎭 Philosophie & Identité Visuelle

**L'esthétique "Obsidian Glass"** évoque un cockpit de station spatiale dans le noir absolu :
- **Fond** : Noir profond, presque absolu (`#09090b`) — pas de gris neutre.
- **Surfaces** : Verre fumé avec transparence (`rgba(18,18,20, 0.7)`) et `backdrop-filter: blur`.
- **Accent** : Violet électrique (`#7b39ed`) avec effet de lueur (`glow`) sur les éléments interactifs.
- **Texte** : Blanc cassé chaud (`#e4e4e7`), jamais blanc pur.
- **Énergie** : Micro-animations subtiles (fade, slide, pulse) pour donner vie à l'interface.

**Ce qu'on évite absolument :**
- Blanc pur (`#ffffff`) comme fond ou couleur de texte principale.
- Couleurs génériques (rouge/vert/bleu système sans transparence).
- Angles droits sans border-radius.
- Absence d'animation sur les éléments interactifs.

---

## 🎨 Palette de Couleurs (Tokens CSS)

Toutes les variables sont définies dans `frontend/src/index.css` et accessibles via `var(--nom)`.

### Couleurs Principales

| Token | Valeur | Usage |
| :--- | :--- | :--- |
| `--primary` | `#7b39ed` | Accent principal : boutons, liens, bordures actives, puces |
| `--primary-glow` | `rgba(123, 57, 237, 0.2)` | Lueurs, `box-shadow`, effets de brillance |
| `--secondary` | `#18181b` | Fonds secondaires, avatars inactifs |
| `--bg-dark` | `#09090b` | Fond de page racine (noir absolu) |
| `--sidebar-bg` | `#09090b` | Fond de la sidebar (identique au fond page) |
| `--danger` | `#f43f5e` | États d'erreur, alertes destructrices |

### Couleurs de Surface (Glassmorphism)

| Token | Valeur | Usage |
| :--- | :--- | :--- |
| `--glass-bg` | `rgba(18, 18, 20, 0.7)` | Fond des cartes, bulles de message, modales |
| `--glass-border` | `rgba(255, 255, 255, 0.06)` | Bordures subtiles sur fonds sombres |

### Couleurs de Texte

| Token | Valeur | Usage |
| :--- | :--- | :--- |
| `--text-main` | `#e4e4e7` | Corps de texte, contenu principal |
| `--text-muted` | `#a1a1aa` | Labels, descriptions, métadonnées |

### Recettes Courantes (Non-variables)

```css
/* Fond actif / hover léger */
background: rgba(123, 57, 237, 0.08);
border-color: rgba(123, 57, 237, 0.2);

/* Fond de surface légèrement plus clair */
background: rgba(255, 255, 255, 0.03);

/* Séparateur discret */
border: 1px solid rgba(255, 255, 255, 0.05);

/* Glow fort sur élément actif */
box-shadow: 0 0 20px rgba(123, 57, 237, 0.4);
```

---

## ✍️ Typographie

Trois familles de polices, chacune avec un rôle précis. Les fichiers `.woff2` sont auto-hébergés dans `frontend/public/fonts/`.

| Token | Police | Poids | Usage |
| :--- | :--- | :--- | :--- |
| `--font-display` | `Space Grotesk` | 700 | Titres, labels de section, boutons CTA |
| `--font-body` | `Inter` | 400 / 500 | Corps de texte, paragraphes, inputs |
| `--font-mono` | `JetBrains Mono` | 400 | Code, ThinkingConsole, badges techniques, outputs |

### Règles Typographiques

```css
/* Titres et labels — toujours Space Grotesk */
font-family: var(--font-display);
letter-spacing: -0.02em; /* Légère compression pour look premium */

/* Corps — Inter avec antialiasing forcé */
font-family: var(--font-body);
-webkit-font-smoothing: antialiased;

/* Code et console — JetBrains Mono */
font-family: var(--font-mono);
```

**Échelle de tailles recommandée :**

| Usage | Taille |
| :--- | :--- |
| Label micro (badges, metadata) | `0.65rem` – `0.7rem` |
| Label normal (descriptions) | `0.75rem` – `0.8rem` |
| Corps de texte | `0.9rem` – `1rem` |
| Titre de section | `1rem` – `1.1rem` (Space Grotesk, uppercase, `letter-spacing: 0.08em`) |

---

## 🧩 Composants Clés & Patterns

### Carte / Surface (Glassmorphism)

```css
.ma-carte {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
```

### Bouton Primaire (CTA)

```css
.btn-primary {
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 10px;
  padding: 8px 16px;
  font-family: var(--font-display);
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-primary:hover {
  filter: brightness(1.1);
  box-shadow: 0 4px 20px var(--primary-glow);
  transform: translateY(-1px);
}
```

### Bouton Secondaire / Ghost

```css
.btn-ghost {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--glass-border);
  color: var(--text-muted);
  border-radius: 10px;
  transition: all 0.2s ease;
}
.btn-ghost:hover {
  background: rgba(123, 57, 237, 0.08);
  border-color: rgba(123, 57, 237, 0.3);
  color: var(--text-main);
}
```

### Input de Formulaire

```css
.mon-input {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  color: var(--text-main);
  font-family: var(--font-body);
  padding: 8px 12px;
  outline: none;
  transition: border-color 0.2s ease;
}
.mon-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-glow);
}
```

### Badge / Pill

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.7rem;
  font-family: var(--font-display);
  font-weight: 700;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--glass-border);
  color: var(--text-muted);
}
```

### Barre de Progression (Monitoring)

```css
.metric-bar-bg {
  width: 100%;
  height: 6px;
  min-height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.metric-bar-fill {
  height: 100%;
  background: var(--primary);
  border-radius: 10px;
  transition: width 0.5s ease;
  box-shadow: 0 0 12px var(--primary-glow);
}
/* Warning state (ex: > 80%) */
.metric-bar-fill.warning { background: #f59e0b; }
/* Danger state (ex: > 95%) */
.metric-bar-fill.danger { background: var(--danger); }
```

---

## 🖥️ Layout de l'Application

```
┌─────────────────────────────────────────────────────┐
│  ChatHeader (fixe, top, hauteur ~52px)               │
├──────────────┬──────────────────────────────────────┤
│              │                                       │
│   Sidebar    │        Zone de Chat                   │
│   (240px /   │   ┌─────────────────────────────┐    │
│   collapsed: │   │  ChatMessages (scroll)       │    │
│   52px)      │   └─────────────────────────────┘    │
│              │   ┌─────────────────────────────┐    │
│  [ThreadList]│   │  ChatInput (fixe, bottom)   │    │
│              │   └─────────────────────────────┘    │
│  ──────────  │                                       │
│  [Cockpit]   │                                       │
│  SystemPulse │                                       │
│  + Project   │                                       │
└──────────────┴──────────────────────────────────────┘
```

**Règles de layout critiques :**
- La sidebar utilise `flex-direction: column` avec `margin-top: auto` sur `.sidebar-cockpit` pour le coller en bas.
- Le `ThreadList` doit avoir `flex: 1; overflow-y: auto; min-height: 0` pour ne pas écraser le Cockpit.
- La zone de chat utilise `flex: 1` pour occuper tout l'espace restant.

---

## ✨ Animations & Transitions

### Transitions Standard

```css
/* Micro-interaction (hover) */
transition: all 0.2s ease;

/* Navigation / Layout */
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

/* Barre de progression */
transition: width 0.5s ease;
```

### Animations Globales (définies dans `index.css`)

```css
/* Apparition d'un élément */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Rotation (loaders) */
@keyframes spin {
  to { transform: rotate(360deg); }
}
```

### Règles d'Animation

1.  **Toujours** animer les apparitions de nouveaux éléments avec `fadeIn`.
2.  **Toujours** mettre un `transform: translateY(-1px)` au hover des boutons cliquables.
3.  **Ne jamais** désactiver les transitions sur des éléments interactifs.

---

## 🖥️ ThinkingConsole — Style Terminal

La `ThinkingConsole` a une esthétique **intentionnellement différente** du reste de l'interface. Elle émule un terminal technique pour signaler qu'on est en territoire "expert".

```css
/* Fond noir profond distinct du reste */
background: #09090b;
font-family: var(--font-mono);
font-size: 0.75rem;

/* Bordure latérale accentuée (signature visuelle) */
border-left: 3px solid var(--primary);

/* Labels de catégorie (Intention, Analyse...) */
.thought-label {
  color: var(--primary);
  font-weight: 700;
  font-family: var(--font-mono);
  text-transform: capitalize;
}
```

**Règle** : Ne jamais appliquer `glassmorphism` à la `ThinkingConsole`. Elle doit rester opaque et sombre pour se distinguer visuellement de la réponse finale.

---

## 📐 Espacements & Rayons

| Usage | Valeur recommandée |
| :--- | :--- |
| Rayon petit (badges, inputs) | `8px` |
| Rayon moyen (cartes, boutons) | `12px` – `16px` |
| Rayon grand (modales, bulles) | `20px` |
| Gap entre éléments d'une liste | `6px` – `8px` |
| Padding interne d'une carte | `16px 22px` |
| Padding de section | `12px 16px` |

---

## 🔗 Références dans le Code

| Fichier | Contenu |
| :--- | :--- |
| `frontend/src/index.css` | Tokens CSS, typographie, resets globaux |
| `frontend/src/components/Messages.css` | Bulles de message, listes, tableaux, code blocks |
| `frontend/src/components/Sidebar.css` | Layout sidebar, cockpit, barres de progression |
| `frontend/src/components/ThinkingConsole.css` | Style terminal pour le raisonnement |
| `frontend/src/components/ChatInput.css` | Zone de saisie, boutons d'action |
