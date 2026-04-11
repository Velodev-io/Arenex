# Phase 01: Environment & Persistence - Context

**Gathered:** 2026-04-11
**Status:** Ready for planning

<domain>
## Phase Boundary
This phase establishes the foundational infrastructure required to support the Arenex platform. It transitions the project from a set of script folders into a single, cohesive FastAPI application with a dedicated persistence layer.

**Deliverables:**
- Working PostgreSQL and Redis local services.
- FastAPI project structure with Async SQLAlchemy.
- Initial migrations for User, Agent, and Match models.
</domain>

<decisions>
## Implementation Decisions

### Project Structure
- Single `app/` directory for the main backend.
- `app/models/`: Database models.
- `app/schemas/`: Pydantic models.
- `app/core/`: Configuration and auth setup.

### Database Connection
- Use `AsyncSession` for all DB interactions.
- Implementation of a `get_db` dependency for routes.

### Dependencies
- Add `asyncpg`, `sqlalchemy`, `alembic`, `pydantic-settings`, `redis` (async).

### the agent's Discretion
- Choice of folder naming conventions (following standard FastAPI patterns).
- Specific configuration for Alembic (e.g., `script_location`).
</decisions>

<canonical_refs>
## Canonical References
- `platform/agents/chess/agent.py` — Reference for existing agent logic.
- `.planning/research/STACK.md` — Source of truth for tech stack choices.
</canonical_refs>

<specifics>
## Specific Ideas
- Users must have `id`, `email`, `hashed_password`, `is_active`, `is_superuser`.
- Agents must have `owner_id` (foreign key to User).
</specifics>

<deferred>
## Deferred Ideas
- JWT Auth logic (Move to Phase 2).
- Match Runner logic (Move to Phase 4).
</deferred>

---
*Phase: 01-environment-persistence*
*Context synthesized: 2026-04-11*
