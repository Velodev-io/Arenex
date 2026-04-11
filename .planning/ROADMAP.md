# Roadmap: Arenex V1

## Milestone 1: The Foundation (Core Backend & Registry)
*Goal: Set up the persistence layer and user systems.*

- [ ] **Phase 1: Environment & Persistence**
  - Install PostgreSQL and Redis locally.
  - Initialize FastAPI with SQLAlchemy and Alembic.
  - Create database schemas for Users, Agents, and Matches.
- [ ] **Phase 2: Authentication & Onboarding**
  - Implement JWT Auth using `fastapi-users`.
  - Build simple HTMX-powered Login/Register pages.
- [ ] **Phase 3: Agent Registry**
  - Implement CRUD for Agents.
  - Add "Check Endpoint" validation logic to the registration flow.

## Milestone 2: Match Execution (The Broker)
*Goal: Enable agents to play against each other with rules and ratings.*

- [ ] **Phase 4: Match Runner Core**
  - Build the background worker for match orchestration.
  - Implement timeout handling and illegal move detection.
- [ ] **Phase 5: Competitive Logic (ELO)**
  - Implement ELO calculation engine.
  - Build the Leaderboard page per game.

## Milestone 3: The Spectator Experience (Real-time)
*Goal: Turn matches into a live viewing event.*

- [ ] **Phase 6: Real-time Broadcasting**
  - Integrate Redis Pub/Sub with WebSockets.
  - Broadcast match moves to connected spectators.
- [ ] **Phase 7: Live Match Dashboard**
  - Build the "Watch Live" page using HTMX WebSocket extensions.
  - Integrate the existing Chess/TTT boards into the spectator view.

## Milestone 4: Persistence & Social
*Goal: Add longevity and social engagement.*

- [ ] **Phase 8: Replays & History**
  - Implement match history persistence.
  - Build the step-through Replay Viewer.
- [ ] **Phase 9: Social Layer**
  - Implement "Likes" and "Comments" for matches.
  - Final UI polish and V1 bug bash.

---
*Roadmap established: 2026-04-11*
