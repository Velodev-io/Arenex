# Phase 01: Environment & Persistence - Research

## Technical approach

### 1. Database & ORM
- **Engine:** PostgreSQL 16+.
- **Driver:** `asyncpg` (Required for FastAPI async flow).
- **ORM:** `SQLAlchemy 2.0` with `DeclarativeBase`.
- **Migrations:** `Alembic` initialized with the `async` template.

### 2. Caching & Pub/Sub
- **Engine:** Redis 7+.
- **Driver:** `redis-py` (asyncio support).
- **Usage:** Match move broadcasting and session caching.

### 3. FastAPI Initialization
- **Config:** `pydantic-settings` for `.env` management.
- **Middleware:** `CORSMiddleware` (Crucial for HTMX/Browser interaction).
- **Structure:** `app/main.py` entry point, `app/database.py` for engine setup.

## Key considerations

### Port Conflict Mitigation
The current R&D agents use 8010/8011. The main platform should run on **8000**.
We need to ensure `uvicorn` starts in a way that doesn't conflict with existing agents if they are running.

### Async Migration Pattern
The project uses `asyncpg`, so migrations must use the `async` migration template in Alembic to handle table creation without blocking.

---
*Research synthesized: 2026-04-11*
