# The Path of All Things

## Vibe
**Wabi-Sabi** — imperfection, organic, quiet, cosmic.
The aesthetic embraces the beauty of transience and incompleteness.
Aged paper, ink bleeds, drifting dust, deep silence between stars.

## Tech Stack
- **Vite** — Build tool (Vanilla JS template)
- **Vanilla JS** — No frameworks, direct DOM manipulation
- **Tailwind CSS v4** — Utility-first styling via `@tailwindcss/vite` plugin
- **SortableJS** — Drag-and-drop card ordering

## Context
**Big History** — A timeline spanning from the Big Bang (13.8 billion years ago)
through the formation of Earth, the emergence of life, human civilizations,
and onward to the far future. Players arrange events in chronological order
to trace "The Path of All Things."

## Architecture
- `index.html` — Base layout with minimalist HUD
- `src/main.js` — Game loop, SortableJS logic, level progression
- `src/style.css` — Tailwind directives + Wabi-Sabi custom classes
- `src/data.json` — Big History event database (levels & events)

## Design Tokens
- Background: `#1a1a1a` (deep charcoal/ink)
- Card surface: `#f5f0e8` (aged paper)
- Accent: `#c4a882` (warm gold/sepia)
- Text: `#e8e0d4` (warm off-white)
- Font: EB Garamond (serif)
