# Chess Agent Spec

## Overview
This agent is a FastAPI-based web server that plays Chess. It serves as the "Scaffold" implementation whose core move logic is designed to be autonomously improved and implemented by a Builder Agent.

The server evaluates a chess board state (provided as a FEN string) and returns the optimal next move (in UCI format) along with a string describing its "reasoning" for the move.

## Dependencies
- `fastapi`
- `pydantic`
- `uvicorn`
- `python-chess` (mandatory for all chess logic, board parsing, check detection, and move validation)

## Request and Response Format (REST Contract)

The server exposes two endpoints designed for the Arenex Agent standard:

### 1. `POST /move`
Calculates the next move based on a given board state.

**Input JSON (`MoveRequest`):**
```json
{
  "board": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "your_color": "white",
  "game_id": "optional-string-id"
}
```
*   `board`: The current board position represented as a valid FEN string.
*   `your_color`: The color the agent is playing as (`"white"` or `"black"`).
*   `game_id`: An optional string identifier for the match.

**Output JSON (`MoveResponse`):**
```json
{
  "move": "e2e4",
  "reasoning": "Controlling center square e4"
}
```
*   `move`: The chosen legal move in UCI string format (e.g., "e2e4", "g1f3", "e1g1" for castling).
*   `reasoning`: A plain text string explaining which priority heuristic was used to select the move. This field is required and critical for debugging.

### 2. `GET /health`
Liveness probe endpoint.

**Output JSON:**
```json
{
  "status": "ok",
  "agent": "chess-agent"
}
```

## Error Handling
The `/move` endpoint explicitly handles and returns HTTP 400 Bad Request for the following edge cases:
- If the FEN string is invalid or cannot be parsed by `python-chess`.
- If the game is already over (`is_game_over()`).
- If the FEN indicates it is the opponent's turn, but the request asks for a move for `your_color`.

## Logic and Rules (Priority Strategy)

The move selection logic `choose_move(board)` relies on `python-chess` to evaluate legal moves (`board.legal_moves`). It evaluates moves strictly based on the following prioritized ladder. The first applicable heuristic dictates the move.

**Piece Value Guide:** Pawn=1, Knight=3, Bishop=3, Rook=5, Queen=9, King=1000

1. **Priority 1: Don't move into check**
   - Ensure the selected move does not leave the agent's king in check. (Note: `board.legal_moves` inherently guarantees this).

2. **Priority 2: Checkmate opponent if possible**
   - Simulate each legal move. If a move results in a checkmate (`board.is_checkmate()`), take it.
   - *Reasoning:* "Checkmate in one"

3. **Priority 3: Check opponent (if it leads to a winning position)**
   - Simulate each legal move. If the move delivers a safe check (meaning the opponent cannot immediately capture the attacking piece for free or a net material loss), take it.
   - *Reasoning:* "Delivering check to gain tempo"

4. **Priority 4: Capture the highest-value piece safely**
   - For all capture moves, calculate the net material exchange (Value of Captured Piece - Value of Attacking Piece if it can be recaptured).
   - Take the move with the highest positive net gain.
   - *Reasoning:* "Capturing {piece_type} for material gain (+{net_gain})"

5. **Priority 5: Protect own pieces under attack**
   - Identify pieces currently under attack. Move the highest-value attacked piece to a safe square.
   - *Reasoning:* "Protecting {piece_type} from capture"

6. **Priority 6: Control center squares**
   - Prefer a move that places a piece safely on e4, d4, e5, or d5.
   - *Reasoning:* "Controlling center square {square}"

7. **Priority 7: Develop pieces early**
   - If in the opening (move count < 10), prefer moves involving knights and bishops over queens and rooks, and minimize early pawn pushes unnecessarily.
   - *Reasoning:* "Developing {piece_type} in the opening"

8. **Priority 8: Castle if possible**
   - If castling rights are available and it is a legal move, do it.
   - *Reasoning:* "Castling for king safety"

9. **Priority 9: Avoid moving the same piece twice in the opening**
   - If in the opening (move count < 10), track moved pieces and deprioritize moving them again.
   - *Reasoning:* "Preferring undeveloped piece"

10. **Priority 10: Fall back to a random legal move**
    - If no other heuristic strongly applies, pick a random legal move from `board.legal_moves`.
    - *Reasoning:* "No strong heuristic applies, choosing randomly"

## How to Run

Ensure dependencies are installed:
```bash
pip install fastapi uvicorn pydantic python-chess
```

Run the server on port 8001:
```bash
uvicorn chess_agent:app --host 0.0.0.0 --port 8001
```
