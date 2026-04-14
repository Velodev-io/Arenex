# Phase 8: Replays & History - Context

**Gathered:** 2026-04-12
**Status:** Planning
**Source:** Roadmap REQ-SPEC-03

<domain>
## Phase Boundary

Transform the existing spectator view into a full-featured replay system. This allows users to review completed matches move-by-move and analyze bot performance.

</domain>

<decisions>
## Implementation Decisions

### Frontend: Replay Controller
- Add playback controls (Back, Forward, Play/Pause, First/Last).
- Implement a `reviewMode` state in `Spectator.jsx`.
- When in `reviewMode`, high-priority WebSocket `move` events should still be added to the history list but should *not* update the current board view unless the user is at the "latest" move.

### Frontend: Interactive Move List
- Every move in the sidebar should be clickable to jump the board to that move's state.

### Frontend: Replay Initialization
- When loading a 'finished' match, default to showing the final state, but enable the replay controls.

</decisions>

<canonical_refs>
## Canonical References
- `frontend/src/pages/Spectator.jsx` — Primary target for enhancement.
- `app/models/__init__.py` — Match model source of truth.

</canonical_refs>

<specifics>
## Specific Ideas
- Use a slider/scrubber for long matches.
- Highlight the "active" move in the sidebar list.

</specifics>

<deferred>
## Deferred Ideas
- Multi-game branching (analysis mode).
- Exporting replays to GIF/Video.

</deferred>

---

*Phase: 08-replays-history*
*Context gathered: 2026-04-12*
