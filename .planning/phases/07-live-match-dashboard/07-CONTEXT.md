# Phase 7: Live Match Dashboard - Context

**Gathered:** 2026-04-12
**Status:** Ready for planning
**Source:** PRD Express Path (User Request)

<domain>
## Phase Boundary

Build a modern React + Vite frontend for the Arenex platform. This phase delivers a centralized dashboard for spectating matches, managing agents, and viewing leaderboards, replacing all legacy local HTML files.

</domain>

<decisions>
## Implementation Decisions

### Tech Stack
- **Framework**: React 18 + Vite.
- **Styling**: Plain CSS (No Tailwind, no component libraries).
- **Chess Logic**: `chess.js` for board state and rule validation.
- **Chess Rendering**: `chessboard.js` (or React-friendly equivalent if preferred, but user specified chessboard.js).
- **Communication**: Native WebSocket API for real-time streams; `fetch()` for REST APIs.

### Page: Home (/)
- List live and completed matches.
- Components to show: agent names, game types, ELO, and status.
- Primary navigation to spectator views.

### Page: Spectator (/match/:id)
- Read-only game board (Chess/TTT).
- WebSocket connection to `ws://localhost:8000/ws/matches/:id`.
- Catch-up logic for initial state.
- Animation on move events.
- Sidebar: Move history, captured pieces, bot reasoning.
- Social: Like button and comments section.

### Page: Leaderboard (/leaderboard)
- Sorted table of agents by ELO.
- Game type filtering.

### Page: Registration (/register)
- Form to add new agents (name, URL, game type).
- Health check validation status feedback.

### Page: Match Orchestration (/start-match)
- Form to initiate matches between compatible agents.
- Post-creation redirect to spectator mode.

### Design & Aesthetics
- **Theme**: Dark Mode (Background: `#1a1a2e`, Accent: `#BB86FC`).
- **Feel**: Clean, minimal, premium.
- **Responsiveness**: Desktop-first (Mobile not required for V1).

### Infrastructure
- Environment variables: `VITE_API_URL` and `VITE_WS_URL`.
- Project root: `frontend/`.

</decisions>

<canonical_refs>
## Canonical References

### Backend API
- `app/main.py` — Router registration.
- `app/api/agents.py` — Agent registry endpoints.
- `app/api/matches.py` — Match creation and history endpoints.
- `app/api/ws.py` — WebSocket match stream logic.
- `app/schemas/` — JSON request/response structures.

### Game Logic Reference
- `app/services/match_runner.py` — Reference for how the backend handles moves and state.

</canonical_refs>

<specifics>
## Specific Ideas
- Use native `EventSource` or `WebSocket` for real-time updates to minimize bundle size.
- Ensure the TTT grid is styled as a premium component, not just a plain table.

</specifics>

<deferred>
## Deferred Ideas
- Mobile responsiveness.
- Account profile settings.
- Advanced social features (avatars, nested comments).

</deferred>

---

*Phase: 07-live-match-dashboard*
*Context gathered: 2026-04-12 via PRD Express Path*
