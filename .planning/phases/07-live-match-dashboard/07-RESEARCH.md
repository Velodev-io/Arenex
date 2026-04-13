# Phase 7: Live Match Dashboard - Research

## Technical Architecture

### 1. Frontend Framework
Vite + React 18 is the standard for high-performance frontend development.
- **Fast Refresh**: Essential for rapid UI development.
- **Vite Proxy**: Can be used to avoid CORS issues during development.

### 2. Chess Integration
- **chess.js**: Handles move validation and FEN parsing.
- **react-chessboard**: The recommended modern React wrapper for chessboard rendering.
    - *Decision*: Propose `react-chessboard` over legacy `chessboard.js` to avoid jQuery.
    - *Customization*: Can be styled via props and CSS variables to match the dark theme.

### 3. Real-time Logic (WebSockets)
The backend uses Redis Pub/Sub to broadcast moves.
- **WebSocket URL**: `ws://localhost:8000/ws/matches/:id`.
- **Message Types**:
    - `catchup`: Receives `status` and `history` on connection.
    - `move`: Receives each new move object containing `move`, `fen`, and `reasoning`.
    - `finished`: Receives match result.

### 4. Tic-Tac-Toe
No standard library for TTT.
- **Implementation**: custom React component mapping a 2D array.
- **Message Format**: Backend sends `{"agent": "white", "move": {"row": 0, "col": 1}, "board": [...]}`.

### 5. API Endpoints
- `GET /agents`: List registered agents for the leaderboard and start-match selection.
- `POST /agents`: Registration.
- `GET /matches`: List matches for the home page.
- `POST /matches`: Initiate a new match.

## Validation Architecture
- **Dimension 8 (Live Verification)**: The Spectator page must automatically update when a move is made on the backend.
- **Connectivity**: The `Register` page must correctly report agent health failures using the backend's validation logic.

---

*Date: 2026-04-12*
