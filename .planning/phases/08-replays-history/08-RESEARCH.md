# Phase 8: Replays & History - Research

## Technical approach

### 1. State Management for Playback
We need to introduce a `viewerIndex` state in `Spectator.jsx`.
- When `viewerIndex === history.length`, we are in "Live Mode". New moves update the index.
- When `viewerIndex < history.length`, we are in "Review Mode". New moves are appended to `history` but don't change `viewerIndex`.

### 2. Playback Controls
Implementing a simple `useInterval` or `useEffect` based timer for auto-play:
- `isAutoPlaying`: boolean state.
- `playbackSpeed`: default 1000ms.

### 3. Interactive History
Each `history` item in the list will have an `onClick={() => setViewerIndex(idx)}` handler.
We will add a "Reviewing Move X" indicator to help user orientation.

### 4. Database Persistence
The `Match.history` field is already updated at every move in `match_runner.py`. No backend changes are strictly necessary, but we should verify that `JSON` history remains consistent between Chess and TTT.

## Verification Strategy
- **Manual Verification**: Launch a match, wait for it to finish, and then use the UI to step back to move 1.
- **Auto-Play Test**: Click "Play" and ensure the board advances through moves.
- **Live Interference Test**: Start a live match, scroll back to move 1, and ensure the board *doesn't* jump to the end when a new move arrives from the WebSocket.

---

*Date: 2026-04-12*
