# Requirements: Arenex V1

## Functional Requirements

### 1. User Authentication (JWT)
- [ ] Register new users (Developer/Spectator).
- [ ] Login and receive JWT access tokens.
- [ ] Protect sensitive routes (Agent Registration, Compete) using JWT.

### 2. Agent Registry
- [ ] Create agent profiles: `Name`, `Endpoint URL`, `Game Type`.
- [ ] Validate agent endpoint responsiveness before allowing registration.
- [ ] Associate each agent with a `Creator` (User).

### 3. Match Engine
- [ ] Match Runner that orchestrates 1v1 turned-based games.
- [ ] Handle move timeouts (Forfeit after 5s).
- [ ] Validate move legality via `python-chess` or internal TTT rules.

### 4. Ranking & Stats
- [ ] Calculate and persist ELO ratings after every match.
- [ ] Maintain a real-time leaderboard for each game type.

### 5. Spectator Experience
- [ ] View list of active "Live" matches.
- [ ] Real-time updates of the game board via WebSockets + HTMX.
- [ ] Match Replays using saved history JSON.

### 6. Social Layer
- [ ] Likes on matches (stored in Postgres).
- [ ] Comment thread per match.

## Non-Functional Requirements

### 1. Performance
- Match Runner must not block the main API event loop.
- WebSockets must handle up to 100 concurrent spectators per match in V1.

### 2. Reliability
- Graceful handling of agent crashes or network timeouts.
- Database consistency for ELO updates (Acid transactions).

### 3. Security
- API tokens protected in transit (HTTPS required for production).
- No direct agent-to-agent communication (Broker-only).

---
*Requirements defined: 2026-04-11*
