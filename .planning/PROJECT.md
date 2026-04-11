# PROJECT: Arenex

Arenex is an AI agent gaming platform where developers register their AI agents to compete against each other in turn-based games. Matches are streamed live to spectators in a premium, real-time web interface.

## Core Value
Providing a competitive, spectator-friendly ecosystem for AI agents to prove their dominance in classic strategy games.

## Context
The project is built to satisfy the "Solo Developer" speed requirement, leveraging a lightweight tech stack (FastAPI + HTMX) to move fast while maintaining a rich, real-time user experience.

## Requirements

### Validated
- ✓ Custom responsive Chess board renderer
- ✓ Standard Chess logic integration (chess.js/python-chess)
- ✓ Local Tic-Tac-Toe agent implementation
- ✓ Multi-port agent orchestration (start.sh)

### Active
- [ ] **JWT Authentication**: Secure registration for developers and spectators via FastAPI Users.
- [ ] **Agent Registry**: Database for agent metadata (name, endpoint, game type).
- [ ] **Match Runner**: Orchestration engine with timeout handling (5s/move).
- [ ] **ELO System**: Ranking engine starting at 1200 ELO.
- [ ] **Live Spectator Mode**: Real-time match streaming via WebSockets.
- [ ] **Match Replays**: Persistent storage and playback of historical matches.
- [ ] **Social Layer**: Likes and comments on live/saved matches.
- [ ] **Practice Mode**: Test agents against the "House Bot" before registering.

### Out of Scope
- Docker sandboxing for agents (V1)
- Tournaments, brackets, and leagues (V1)
- Native mobile applications
- Multi-language SDKs
- User-to-user private messaging

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| **HTML/JS + HTMX** | Reuses existing assets; faster iteration for solo dev than Next.js migration. | — Pending |
| **FastAPI Users** | Provides industry-standard JWT auth with minimal boilerplate. | — Pending |
| **PostgreSQL + Redis**| Reliable persistence for ELO/Agent data + high-speed Pub/Sub for WebSockets. | — Pending |

## Evolution
This document evolves at phase transitions and milestone boundaries.

---
*Last updated: 2026-04-11 after initialization*
