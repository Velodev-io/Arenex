# Testing Strategy - Arenex

**Analysis Date:** 2026-04-11

## Test Environment

**Tooling:**
- Uses custom Python scripts instead of standard PyTest/Unittest for specialized game testing.
- **Mocking:** LLM calls are mocked in certain testing scenarios to verify internal logic flow.

## Verification Workflow

**1. Code Integrity:**
- `ChessAgent/chess_tester.py`: Evaluates the bot's move quality against benchmark positions.
- `Tic-Tac-ToeAgent/test_agent.py`: Validates winning/losing/drawing logic.

**2. UI/UX Verification:**
- Manual browser testing of `index.html`.
- Verification of piece rendering on different viewport sizes.

**3. Integration Testing:**
- Running `platform/start.sh` and ensuring all agents bind to their specific ports (8010, 8011) and respond to `/health`.

---
*Testing analysis: 2026-04-11*
