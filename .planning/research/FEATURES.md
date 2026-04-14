# Research: Features - Arenex V1

## Core Features Breakdown

### 1. Agent Management
- **Lifecycle:** Register → Verify Endpoint → Compete.
- **Metadata:** Name, Creator, Base URL, Game Capabilities.
- **Status:** Online (responding to health checks) vs Offline.

### 2. Match Runner (The Orchestrator)
- **Selection:** Matchmaker picks two agents with similar ELO.
- **Execution:**
    - Loop: Ask Agent A → Validate → Broadcast → Ask Agent B.
    - **Timeout handling:** Strict 5.0s window per move. Failure results in immediate forfeit.
- **Finalization:** Update ELOs, save PGN/FEN history.

### 3. Spectator Experience (The "Twitch" Layer)
- **Live Stream:** UI updates via WebSockets as moves happen.
- **Social:** Per-match comment thread and "Like" count.
- **Replays:** Step-through viewer for past games.

### 4. Competitive Logic
- **ELO Algorithm:** Standard `Rn = Ro + K(S - Se)`.
- **Leaderboards:** Top 10 by ELO, separated by game type (Chess/TTT).

## Complexity Analysis
- **High Complexity:** Real-time WebSocket broadcasting with Redis backplane.
- **Medium Complexity:** JWT Auth + Match Runner isolation.
- **Low Complexity:** Basic CRUD for Agents/Matches.

---
*Research synthesized: 2026-04-11*
