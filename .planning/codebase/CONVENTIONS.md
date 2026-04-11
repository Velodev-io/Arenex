# Coding Conventions - Arenex

**Analysis Date:** 2026-04-11

## Python Conventions

**Style:**
- Follows PEP 8 where applicable.
- Uses `FastAPI` for all backend services.
- Models are defined using `Pydantic` for strict typing.

**Move Logic:**
- AI moves are returned in **UCI format** (e.g., `e2e4`).
- Board states are communicated via **FEN strings**.
- **Rule of Safety:** Agents MUST validate moves locally before returning them to the UI.

## JavaScript Conventions

**UI Patterns:**
- Responsive layouts using `100dvh` and CSS `min()`/`calc()`.
- Two-click move system (Select → Target) instead of Drag & Drop.
- **Contrast Check:** Pieces must have shadows/outlines for visibility on light squares.

## AI Logic Patterns

**Reasoning:**
- Every move returned by an agent must include a `reasoning` string for user transparency.
- Heuristics are prioritized over raw random moves.

---
*Conventions analysis: 2026-04-11*
