# Research: Pitfalls - Arenex V1

## Common Domain Risks

### 1. Agent Timeout & Zombies
- **Risk:** An agent might hang for >5s, blocking the match runner.
- **Prevention:** Use `httpx` with strict `timeout` settings in the Python backend. If an agent fails to respond, forfeit the match instantly.

### 2. Race Conditions in Move Submission
- **Risk:** Both agents submitting moves out of turn (unlikely in turn-based, but possible if the broker is slow).
- **Prevention:** State tracking in the Match Runner. Only accept input from the `turn` color.

### 3. ELO Inflation/Gaming
- **Risk:** A developer registering two agents and letting one lose repeatedly to boost the other.
- **Prevention:** Limit matches between the same two agents within a 1-hour window.

### 4. WebSocket "Storms"
- **Risk:** Thousands of spectators join a popular match, overwhelming the server.
- **Prevention:** Use HTMX with WebSocket extensions to handle efficient partial DOM swaps. Don't send the whole page, just the updated "Move" JSON.

### 5. "File://" Protocol Security (Frontend)
- **Risk:** Browser security blocking assets during transition.
- **Prevention:** All assets should now be served by the FastAPI static file server (`/static`) instead of opened via `file://`.

---
*Research synthesized: 2026-04-11*
