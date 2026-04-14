# Chess Agent — Platform Spec

## Overview
A FastAPI server that plays chess using `python-chess` for all move generation and validation. This is the house bot for the Arenex platform. It serves the same REST contract as the Tic-Tac-Toe agent.

**Runs on port `8001`.**

## Dependencies
- `fastapi`
- `uvicorn`
- `pydantic`
- `python-chess`
- `fastapi.middleware.cors` (built-in with FastAPI)

## Request and Response Format

### `POST /move`

**Input JSON:**
```json
{
  "board": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "your_mark": "white",
  "game_id": "optional-string"
}
```

> Note: field is `your_mark` (not `your_color`) to stay consistent with the tic-tac-toe agent contract.

**Output JSON:**
```json
{
  "move": "e2e4",
  "reasoning": "Controlling center square e4"
}
```

### `GET /health`
```json
{ "status": "ok", "agent": "chess-agent" }
```

## CORS — Mandatory

The agent MUST include this middleware or the browser will block all requests:

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Logic and Rules (Priority Strategy)

`choose_move(board: chess.Board)` evaluates moves using `python-chess` primitives only. Evaluate in strict priority order — take the first rule that applies.

**Piece Values:** Pawn=1, Knight=3, Bishop=3, Rook=5, Queen=9, King=1000

1. **Don't move into check**
   - `board.legal_moves` guarantees this inherently. No additional check needed.

2. **Checkmate opponent if possible**
   - For each legal move: `board.push(move)`, check `board.is_checkmate()`, then `board.pop()`.
   - If found: return that move.
   - Reasoning: `"Checkmate in one"`

3. **Capture highest-value piece safely**
   - For all `board.is_capture(move)` moves: calculate net gain = value of captured piece - value of attacker (if board position after move leaves our piece attacked).
   - Select the move with highest positive net gain.
   - Reasoning: `"Capturing {piece_type} for material gain"`

4. **Protect hanging pieces**
   - Check which of our own pieces are currently attacked by the opponent.
   - For the highest-value attacked piece, find a safe square to move it to.
   - Reasoning: `"Protecting {piece_type} from capture"`

5. **Control center squares**
   - Prefer moves that place a piece safely on `e4, d4, e5, d5`.
   - Reasoning: `"Controlling center square {square}"`

6. **Develop minor pieces early**
   - If `board.fullmove_number < 10`, prefer moves involving knights and bishops over queens, rooks, and pawns.
   - Reasoning: `"Developing {piece_type} in the opening"`

7. **Castle if available**
   - If `board.has_castling_rights(color)` and castling is in `board.legal_moves`.
   - Reasoning: `"Castling for king safety"`

8. **Avoid moving same piece twice in opening**
   - If `board.fullmove_number < 10`, prefer pieces that have not yet moved.
   - Reasoning: `"Preferring undeveloped piece"`

9. **Any legal move as fallback**
   - Pick a random legal move from `list(board.legal_moves)`.
   - Reasoning: `"No strong heuristic applies, choosing randomly"`

## Error Handling — `POST /move`
Return HTTP `400` for:
- Invalid FEN string (wrap `chess.Board(fen)` in try/except)
- Game already over (`board.is_game_over()`)
- Wrong side to move (FEN says black's turn but `your_mark` is `"white"`)

## How to Run
```bash
uvicorn agent:app --host 0.0.0.0 --port 8001
```
