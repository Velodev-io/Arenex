# Phase 9: Social Layer & Practice Mode - Research

## Technical Architecture

### 1. Anonymous Social Backend
- **Database**:
  - `MatchLike`: Simple table to store like events. `POST /matches/{id}/like` increments.
  - `Comment`: `display_name` + `content`. `GET /matches/{id}/social` returns both.
- **REST APIs**:
  - `POST /matches/{id}/like`
  - `POST /matches/{id}/comment`
  - `GET /matches/{id}/social`: Returns likes count and list of comments.

### 2. Practice Mode: "User vs House Bot"
- **The "User Move" Endpoint**:
  - `POST /matches/{id}/move`:
    - Validates that the match is a `practice` match.
    - Validates user move (UCI for chess, row/col for TTT).
    - Updates history.
    - Triggers "House Bot" move immediately.
- **The House Bot**:
  - **Chess**: Uses `random.choice(list(board.legal_moves))`.
  - **TTT**: Picks a random empty cell.
- **Broadcasting**:
  - Both User and Bot moves are broadcasted via the existing WebSocket logic.

### 3. Frontend Playability
- **Chess**: `react-chessboard` `onPieceDrop` prop.
  - Validates move locally using `chess.js`.
  - Sends UCI to backend.
- **TTT**: `onClick` handler on custom grid.
- **New Route**: `/practice` to select game type and start.

## UI/UX Wow Factors
- **Toast Notifications**: For "Your Turn", "Bot Thinking", and "Illegal Move".
- **Social Feed**: A sidebar component in Replay/Spectator that shows a scrolling list of anonymous comments.

## Verification Strategy
- **Social**: Verify guest users can like and comment.
- **Practice**: Play a full game of Chess and TTT against the bot and ensure completion results in a "Finished" state.

---

*Date: 2026-04-12*
