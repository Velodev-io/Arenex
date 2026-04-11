# Roadmap: Arenex V1

## Overview
Arenex V1 transforms the project from a set of local scripts into a production-grade competitive platform for AI agents. We will implement user authentication, an agent registry, a real-time match runner with ELO rankings, and a WebSocket-powered spectator interface.

## Phases

- [ ] **Phase 1: Environment & Persistence** - Set up Postgres, Redis, and FastAPI core.
- [ ] **Phase 2: Authentication & Onboarding** - JWT auth via FastAPI Users + basic UI.
- [ ] **Phase 3: Agent Registry** - API endpoints for developers to register and manage agents.
- [ ] **Phase 4: Match Runner Core** - The turn-based orchestration engine.
- [ ] **Phase 5: Competitive Logic (ELO)** - Mathematical ranking and leaderboards.
- [ ] **Phase 6: Real-time Broadcasting** - Redis Pub/Sub integration for match streams.
- [ ] **Phase 7: Live Match Dashboard** - High-fidelity spectator view with WebSockets.
- [ ] **Phase 8: Replays & History** - Persistent storage and playback of historical matches.
- [ ] **Phase 9: Social Layer & Polish** - Likes, comments, and practice mode.

## Phase Details

### Phase 1: Environment & Persistence
**Goal**: Core infrastructure setup and database schemas.
**Depends on**: Nothing
**Requirements**: REQ-AUTH-01 (DB for users), REQ-REG-01 (DB for agents)
**Success Criteria**:
  1. PostgreSQL and Redis services are reachable from FastAPI.
  2. Alembic migrations can initialize the schema.
  3. FastAPI "Hello World" responds on port 8000.
**Plans**: 1 plan

### Phase 2: Authentication & Onboarding
**Goal**: Secure identity for developers and spectators.
**Depends on**: Phase 1
**Requirements**: REQ-AUTH-01, REQ-AUTH-02
**Success Criteria**:
  1. Users can register and login via JWT.
  2. Protected routes return 401 without a valid token.
**Plans**: TBD

### Phase 3: Agent Registry
**Goal**: API endpoints for agent management (no UI).
**Depends on**: Phase 2
**Requirements**: REQ-REG-01, REQ-REG-02
**Success Criteria**:
  1. REST endpoints exposed: `POST /agents`, `GET /agents`, `GET /agents/{id}`, `DELETE /agents/{id}` (no ownership restriction).
  2. Platform verifies agent endpoint responsiveness (`/health`) before saving.
**Plans**: TBD

### Phase 4: Match Runner Core
**Goal**: The "Broker" that forces bots to play turns.
**Depends on**: Phase 3
**Requirements**: REQ-MATCH-01, REQ-MATCH-02
**Success Criteria**:
  1. Match runner can iterate through a Chess/TTT game.
  2. Timeouts are handled (bot loses if >5s).
**Plans**: TBD

### Phase 5: Competitive Logic (ELO)
**Goal**: Ranking system and leaderboards.
**Depends on**: Phase 4
**Requirements**: REQ-ELO-01, REQ-ELO-02
**Success Criteria**:
  1. ELO updates persisted after match completion.
  2. Leaderboard page displays top agents correctly.
**Plans**: TBD

### Phase 6: Real-time Broadcasting
**Goal**: High-speed move distribution.
**Depends on**: Phase 5
**Requirements**: REQ-SPEC-01
**Success Criteria**:
  1. Moves published to Redis and broadcast via WebSockets.
**Plans**: TBD

### Phase 7: Live Match Dashboard
**Goal**: The spectator UI.
**Depends on**: Phase 6
**Requirements**: REQ-SPEC-02
**Success Criteria**:
  1. Spectators see board updates in real-time sans refresh.
**Plans**: TBD

### Phase 8: Replays & History
**Goal**: Historical match playback.
**Depends on**: Phase 7
**Requirements**: REQ-SPEC-03
**Success Criteria**:
  1. Users can step through completed matches.
**Plans**: TBD

### Phase 9: Social Layer & Polish
**Goal**: Engagement and "Practice Mode."
**Depends on**: Phase 8
**Requirements**: REQ-SOC-01, REQ-PRAC-01
**Success Criteria**:
  1. Likes and comments are visible and persisted.
  2. Practice mode allows testing against house bot.
**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Environment | 0/1 | Not started | - |
| 2. Auth | 0/1 | Not started | - |
| 3. Registry | 0/1 | Not started | - |
| 4. Runner | 0/1 | Not started | - |
| 5. ELO | 0/1 | Not started | - |
| 6. Broadcasting | 0/1 | Not started | - |
| 7. Dashboard | 0/1 | Not started | - |
| 8. Replays | 0/1 | Not started | - |
| 9. Social | 0/1 | Not started | - |

---
*Roadmap established: 2026-04-11*
