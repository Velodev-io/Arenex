# Research: Stack - Arenex V1

**Target Stack:** FastAPI + HTMX + PostgreSQL + Redis

## Backend
- **Framework:** `FastAPI` — Essential for handling the asynchronous nature of WebSocket streams and concurrent agent requests.
- **Authentication:** `FastAPI-Users` — Standard JWT-based auth. It supports pluggable database adapters and handles password hashing out of the box.
- **ORM:** `SQLAlchemy` (Async) with `Alembic` for migrations.
- **Task Queue:** `BackgroundTasks` (standard FastAPI) for non-blocking match processing.

## Database & Caching
- **Primary DB:** `PostgreSQL` — Relational storage for Agents, Users, Matches, and ELO history.
- **Pub/Sub & Real-time:** `Redis` — Required for broadcasting live match moves to all connected WebSocket clients efficiently.

## Frontend
- **Framework:** `HTMX` — Replaces complex reactive frontend logic. Handles "Live" updates via WebSocket extensions or polling.
- **Styling:** Vanilla CSS (Modern CSS Grid/Flexbox).
- **Interactions:** Vanilla JS (reusing existing Chess/TTT renderer).

## Communication
- **REST:** Agent registration and move submission.
- **WebSockets:** Live match streaming.
- **UCI/FEN:** Standard chess communication formats.

---
*Research synthesized: 2026-04-11*
