# System Architecture - Arenex

**Analysis Date:** 2026-04-11

## High-Level Pattern

Arenex follows a **Decoupled Agent-Host Architecture**. The frontend is a "dumb" viewer that holds the game board and state, while the backend "Agents" provide the specific intelligence and rule validation for each game.

## Key Layers

**1. Display Layer (Frontend):**
- Static HTML/CSS/JS.
- Handles board rendering and user interaction.
- Communicates with agents via standard HTTP POST `/move` requests.

**2. Orchestration Layer (`platform/start.sh`):**
- Powers on the entire platform.
- Handles concurrency (running multiple FastAPI servers).
- Acts as the process manager for the gaming session.

**3. Intelligence Layer (Backend Agents):**
- Game-specific logic (Chess vs Tic-Tac-Toe).
- Move validation ensures no illegal moves reach the board.
- AI logic (Heuristics or LLM) to choose the next move.

## Data Flow

1. **User Input:** Player clicks a piece and a destination square on the UI.
2. **Move Validation (Local):** `chess.js` validates move on the client.
3. **Agent Request:** UI sends FEN/Board string to Agent.
4. **Agent Logic:** AI chooses move → `python-chess` validates move for safety.
5. **Response:** Agent returns Move (UCI) + Reasoning.
6. **Update:** UI applies bot move and updates board state.

---
*Architecture analysis: 2026-04-11*
