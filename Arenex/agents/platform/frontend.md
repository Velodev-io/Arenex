# Frontend — Platform Spec

## Overview
Three static HTML pages that form the Arenex local gaming platform. No build step — pure HTML, CSS, and vanilla JS. Chess uses CDN-hosted libraries. Tic-tac-toe logic runs entirely in the browser with no external dependencies.

## File Structure
```
platform/
└── frontend/
    ├── index.html       # Game selector + win/loss stats
    ├── tictactoe.html   # Tic-tac-toe board + bot integration
    └── chess.html       # Chess board + bot integration
```

## Shared Design Rules
- Dark themed, minimal, and clean.
- Consistent nav header: show "Arenex" logo, and a back-link to `index.html`.
- Loading state while waiting for bot response (spinner or text).
- Bot reasoning is displayed below the board after every bot move.

---

## Page 1: `index.html` — Game Selector

### What it does
- Landing page with two large clickable cards/buttons.
- Clicking "Play Tic-tac-toe" links to `tictactoe.html`.
- Clicking "Play Chess" links to `chess.html`.
- Displays the user's personal win/loss record per game, read from `localStorage`.

### localStorage Keys
- `ttt_wins`, `ttt_losses`, `ttt_draws`
- `chess_wins`, `chess_losses`, `chess_draws`

### Layout
- Centered vertically and horizontally.
- Two cards side by side, each showing: game name, emoji icon, and `W: X / L: X / D: X` stat line.

---

## Page 2: `tictactoe.html` — Tic-Tac-Toe

### What it does
- Shows an interactive 3x3 tic-tac-toe grid.
- Player clicks a cell to place their mark. Empty cells are clickable.
- After the player's move, the frontend calls `POST http://localhost:8000/move` with the current board state.
- Bot response applies the bot's move to the grid and displays the `reasoning` text below the board.
- Detects win/draw/loss. Updates `localStorage` stats when game ends.
- Has a "New Game" button that resets the board and randomly assigns who goes first (player or bot).

### Bot API Call
```javascript
fetch("http://localhost:8000/move", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    board: board,      // 3x3 array, "" for empty, "X" or "O" for marks
    your_mark: botMark, // "X" or "O"
    game_id: gameId
  })
})
```

### Board State Representation
- `board`: 3x3 array of strings. Empty cell = `""`. Player = `"X"`. Bot = `"O"` (or reversed on random assignment).
- Bot response: `{ row: int, col: int, reasoning: string }`

### Bot Side Assignment
- On new game: `Math.random() < 0.5` → player is X (goes first), else player is O (goes second).
- If bot goes first, immediately call `/move` with the empty board.

### Win Detection (browser-side only)
- Check all 8 lines (3 rows, 3 cols, 2 diagonals) after every move.
- If all 3 in a line match a non-empty mark: that mark wins.
- If board is full and no winner: draw.

---

## Page 3: `chess.html` — Chess

### What it does
- Shows a full chess board using `chessboard.js` + `chess.js` from CDN.
- Player drags pieces to make a move. `chess.js` validates all moves client-side.
- After a valid player move: get current FEN from `chess.js`, call `POST http://localhost:8001/move`.
- Bot response: apply the UCI move to the board using `chess.js`. Reflect move on `chessboard.js` board.
- Display: reasoning text, move history list, captured pieces list.
- "New Game" button resets and randomly assigns player as white or black.

### CDN Libraries (load in HTML head)
```html
<link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css">
<script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js"></script>
<script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
```

### Bot API Call
```javascript
fetch("http://localhost:8001/move", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    board: game.fen(),      // FEN string from chess.js
    your_mark: botColor,    // "white" or "black"
    game_id: gameId
  })
})
```

### Bot Response Handling
- Bot returns `{ move: "e2e4", reasoning: "..." }` (UCI format).
- Apply with `game.move({ from: move.slice(0,2), to: move.slice(2,4), promotion: "q" })`.
- Re-render board with `board.position(game.fen())`.

### Side Panel
Show alongside the board:
- Move history: list of moves in algebraic notation as the game progresses.
- Captured pieces: icons or letters of pieces each side has captured.
- Reasoning box: last bot reasoning string, updated after every bot move.

### Game End
- Detect: `game.game_over()`, `game.in_checkmate()`, `game.in_draw()`, `game.in_stalemate()`.
- Show a banner with result ("You won!", "Bot wins!", "Draw!").
- Update `chess_wins / chess_losses / chess_draws` in `localStorage`.

## How to Open
No server needed. Open directly in a browser:
```bash
open platform/frontend/index.html
```
