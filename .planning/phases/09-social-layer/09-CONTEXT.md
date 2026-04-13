# Phase 9: Social Layer & Practice Mode - Context

**Gathered:** 2026-04-12
**Status:** Planning
**Source:** User Request (Revised Scope)

<domain>
## Phase Boundary

Finalize the current roadmap by adding spectator engagement (Likes & Comments) and a playable "Practice Mode" for new users to test the platform without needing an agent.

</domain>

<decisions>
## Implementation Decisions

### 1. Anonymous Social Layer
- **Likes**: Registered in a `MatchLike` table. No user authentication required.
- **Comments**: Registered in a `Comment` table with a mandatory `display_name` field.
- **UI**: Added to both Live Spectator and Replay views.

### 2. Practice Mode (User vs Bot)
- **Flow**:
  1. User starts a practice match (Chess or TTT).
  2. UI displays an interactive (draggable) board.
  3. User makes a move -> UI calls `POST /matches/{id}/user-move`.
  4. Backend validates move -> updates DB -> triggers "House Bot" calculation.
  5. House Bot move is registered -> broadcast via WebSocket.
- **House Bot Strategy**:
  - Chess: Picks a random legal move or basic capture-preferred move.
  - TTT: Random available cell.

### 3. Database Schema Updates
- **Match**: Add `is_practice` boolean flag.
- **Comment**: `match_id`, `display_name`, `content`, `created_at`.
- **MatchLike**: `match_id`, `created_at`.

### 4. Simplified Auth
- No JWT/Login required for these features in V1 as per user request.

</decisions>

<canonical_refs>
## Canonical References
- `app/models/__init__.py`: Schema updates.
- `app/api/matches.py`: Add practice orchestration endpoints.
- `app/services/match_runner.py`: Add bot move logic.
- `frontend/src/pages/Practice.jsx`: New playable page.

</canonical_refs>

<specifics>
## Specific Ideas
- Use a "Toast" notification when an illegal move is attempted in Practice Mode.
- Heart pulse animation for likes.

</specifics>

<deferred>
## Deferred Ideas
- User accounts for social (V2).
- Advanced Stockfish integration (V2).

</deferred>

---

*Phase: 09-social-layer-practice*
*Context gathered: 2026-04-12*
