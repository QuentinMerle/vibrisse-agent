# 🎨 Vibrisse Design System — "Obsidian Glass"

This file is the **visual source of truth** for the project. It must be read by any AI agent before creating or modifying a UI component.

> **Golden Rule**: Never invent a color, spacing, or font on the fly. Everything must be derived from the tokens defined here. When in doubt, consult `frontend/src/index.css`.

---

## 🎭 Philosophy & Visual Identity

**The "Obsidian Glass" aesthetic** evokes a spacecraft cockpit in absolute darkness:
- **Background**: Deep black, almost absolute (`#09090b`) — no neutral grays.
- **Surfaces**: Smoked glass with transparency (`rgba(18,18,20, 0.7)`) and `backdrop-filter: blur`.
- **Accent**: Electric Purple (`#7b39ed`) with a "glow" effect on interactive elements.
- **Text**: Warm off-white (`#e4e4e7`), never pure white.
- **Energy**: Subtle micro-animations (fade, slide, pulse) to bring the interface to life.

**What we strictly avoid:**
- Pure white (`#ffffff`) for backgrounds or primary text.
- Generic colors (system red/green/blue without transparency).
- Sharp 90-degree corners without border-radius.
- Absence of animation on interactive elements.

---

## 🎨 Color Palette (CSS Tokens)

All variables are defined in `frontend/src/index.css` and accessible via `var(--name)`.

### Primary Colors

| Token | Value | Usage |
| :--- | :--- | :--- |
| `--primary` | `#7b39ed` | Main accent: buttons, links, active borders, bullets |
| `--primary-glow` | `rgba(123, 57, 237, 0.2)` | Glows, `box-shadow`, shine effects |
| `--secondary` | `#18181b` | Secondary backgrounds, inactive avatars |
| `--bg-dark` | `#09090b` | Root page background (absolute black) |
| `--sidebar-bg` | `#09090b` | Sidebar background (matches page background) |
| `--danger` | `#f43f5e` | Error states, destructive alerts |

### Surface Colors (Glassmorphism)

| Token | Value | Usage |
| :--- | :--- | :--- |
| `--glass-bg` | `rgba(18, 18, 20, 0.7)` | Card backgrounds, message bubbles, modals |
| `--glass-border` | `rgba(255, 255, 255, 0.06)` | Subtle borders on dark backgrounds |

### Text Colors

| Token | Value | Usage |
| :--- | :--- | :--- |
| `--text-main` | `#e4e4e7` | Body text, primary content |
| `--text-muted` | `#a1a1aa` | Labels, descriptions, metadata |

### Common Recipes (Non-variables)

```css
/* Active background / Light hover */
background: rgba(123, 57, 237, 0.08);
border-color: rgba(123, 57, 237, 0.2);

/* Slightly lighter surface background */
background: rgba(255, 255, 255, 0.03);

/* Discrete separator */
border: 1px solid rgba(255, 255, 255, 0.05);

/* Strong glow on active element */
box-shadow: 0 0 20px rgba(123, 57, 237, 0.4);
```

---

## ✍️ Typography

Three font families, each with a specific role. `.woff2` files are self-hosted in `frontend/public/fonts/`.

| Token | Font | Weight | Usage |
| :--- | :--- | :--- | :--- |
| `--font-display` | `Space Grotesk` | 700 | Titles, section labels, CTA buttons |
| `--font-body` | `Inter` | 400 / 500 | Body text, paragraphs, inputs |
| `--font-mono` | `JetBrains Mono` | 400 | Code, ThinkingConsole, technical badges, outputs |

### Typographic Rules

```css
/* Titles and labels — always Space Grotesk */
font-family: var(--font-display);
letter-spacing: -0.02em; /* Slight compression for premium look */

/* Body — Inter with forced antialiasing */
font-family: var(--font-body);
-webkit-font-smoothing: antialiased;

/* Code and console — JetBrains Mono */
font-family: var(--font-mono);
```

**Recommended Size Scale:**

| Usage | Size |
| :--- | :--- |
| Micro label (badges, metadata) | `0.65rem` – `0.7rem` |
| Normal label (descriptions) | `0.75rem` – `0.8rem` |
| Body text | `0.9rem` – `1rem` |
| Section Title | `1rem` – `1.1rem` (Space Grotesk, uppercase, `letter-spacing: 0.08em`) |

---

## 🧩 Key Components & Patterns

### Card / Surface (Glassmorphism)

```css
.my-card {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
```

### Primary Button (CTA)

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

### Form Input

```css
.my-input {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  color: var(--text-main);
  font-family: var(--font-body);
  padding: 8px 12px;
  outline: none;
  transition: border-color 0.2s ease;
}
.my-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-glow);
}
```

---

## 🖥️ Application Layout

```
┌─────────────────────────────────────────────────────┐
│  ChatHeader (fixed, top, height ~52px)               │
├──────────────┬──────────────────────────────────────┤
│              │                                       │
│   Sidebar    │        Chat Zone                      │
│   (240px /   │   ┌─────────────────────────────┐    │
│   collapsed: │   │  ChatMessages (scroll)       │    │
│   52px)      │   └─────────────────────────────┘    │
│              │   ┌─────────────────────────────┐    │
│  [ThreadList]│   │  ChatInput (fixed, bottom)  │    │
│              │   └─────────────────────────────┘    │
│  ──────────  │                                       │
│  [Cockpit]   │                                       │
│  SystemPulse │                                       │
│  + Project   │                                       │
└──────────────┴──────────────────────────────────────┘
```

**Critical Layout Rules:**
- Sidebar uses `flex-direction: column` with `margin-top: auto` on `.sidebar-cockpit` to pin it to the bottom.
- `ThreadList` must have `flex: 1; overflow-y: auto; min-height: 0` to avoid crushing the Cockpit.
- Chat zone uses `flex: 1` to occupy all remaining space.

---

## ✨ Animations & Transitions

### Standard Transitions

```css
/* Micro-interaction (hover) */
transition: all 0.2s ease;

/* Navigation / Layout */
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

/* Progress bar */
transition: width 0.5s ease;
```

### Animation Rules

1.  **Always** animate the appearance of new elements with `fadeIn`.
2.  **Always** apply a `transform: translateY(-1px)` on hover for clickable buttons.
3.  **Never** disable transitions on interactive elements.

---

## 🖥️ ThinkingConsole — Terminal Style

The `ThinkingConsole` has an aesthetic that is **intentionally different** from the rest of the interface. It emulates a technical terminal to signal that we are in "expert" territory.

**Rule**: Never apply `glassmorphism` to the `ThinkingConsole`. It must remain opaque and dark to visually distinguish it from the final response.

---

## 📐 Spacing & Radii

| Usage | Recommended Value |
| :--- | :--- |
| Small radius (badges, inputs) | `8px` |
| Medium radius (cards, buttons) | `12px` – `16px` |
| Large radius (modals, bubbles) | `20px` |
| Gap between list items | `6px` – `8px` |
| Card internal padding | `16px 22px` |
| Section padding | `12px 16px` |
