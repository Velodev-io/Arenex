# Tic-Tac-Toe Agent Spec

## Overview
This agent is a FastAPI-based web server that plays Tic-Tac-Toe. It implements an invincible, rule-based strategy. It evaluates the current board state and returns the optimal next move along with a "reasoning" string explaining why the move was chosen.

## Request and Response Format

The agent implements two endpoints according to the Arenex Agent REST Contract:

### 1. `POST /move`
Calculates the next move based on the board state.

**Input JSON (`GameState`):**
```json
{
  "board": [
    ["X", "", ""],
    ["", "O", ""],
    ["", "", "X"]
  ],
  "your_mark": "O",
  "game_id": "optional-string-id"
}
```
*   `board`: A 3x3 2D array of strings. Empty cells are represented by `""`. Player marks are `"X"` and `"O"`.
*   `your_mark`: The mark the agent is playing as (`"X"` or `"O"`).
*   `game_id`: An optional string identifier for the match.

**Output JSON (`MoveResponse`):**
```json
{
  "row": 0,
  "col": 1,
  "reasoning": "Blocking opponent's win"
}
```
*   `row`: The 0-indexed row of the chosen move.
*   `col`: The 0-indexed column of the chosen move.
*   `reasoning`: A plain text explanation of the priority rule that was triggered to select this move.

### 2. `GET /health`
A standard liveness probe.

**Output JSON:**
```json
{
  "status": "ok",
  "agent": "rule-based-tictactoe"
}
```

## Logic and Rules (Priority Strategy)

When a board state is received, the agent evaluates possible moves strictly in the following priority order. The first priority condition that is met determines the move.

1.  **Priority 1: Win immediately**
    *   Iterate through all empty cells.
    *   Simulate placing the agent's mark in each empty cell.
    *   If placing the mark creates a winning line (3 in a row horizontally, vertically, or diagonally), choose this cell.
    *   *Reasoning:* "Taking the win"

2.  **Priority 2: Block opponent's winning move**
    *   Iterate through all empty cells.
    *   Simulate placing the *opponent's* mark in each empty cell.
    *   If placing the opponent's mark creates a winning line for the opponent, choose this cell to block them.
    *   *Reasoning:* "Blocking opponent's win"

3.  **Priority 3: Create a fork**
    *   Iterate through all empty cells.
    *   Simulate placing the agent's mark in an empty cell.
    *   Count how many winning opportunities (threats) the agent would have on its *next* turn.
    *   If the move creates 2 or more winning threats, choose this cell (this is a fork).
    *   *Reasoning:* "Creating a fork"

4.  **Priority 4: Block opponent's fork**
    *   Iterate through all empty cells.
    *   Simulate placing the *opponent's* mark in an empty cell.
    *   Check if that move would create 2 or more winning threats for the opponent.
    *   If so, choose this cell to prevent the fork.
    *   *Reasoning:* "Blocking opponent's fork"

5.  **Priority 5: Take center**
    *   Check if the center board cell (row 1, col 1) is empty.
    *   If empty, choose the center.
    *   *Reasoning:* "Taking center"

6.  **Priority 6: Take opposite corner from opponent**
    *   Check the four corners: `(0,0)`, `(0,2)`, `(2,0)`, `(2,2)`.
    *   If the opponent occupies a corner, check if the diagonally opposite corner is empty.
        *   `0,0` is opposite `2,2`
        *   `0,2` is opposite `2,0`
    *   If an opposite corner is empty, choose it.
    *   *Reasoning:* "Taking opposite corner"

7.  **Priority 7: Take any empty corner**
    *   Check the four corners in any order.
    *   If any corner is empty, choose it.
    *   *Reasoning:* "Taking a corner"

8.  **Priority 8: Take any empty side**
    *   Check the four edge/side cells: `(0,1)`, `(1,0)`, `(1,2)`, `(2,1)`.
    *   If any side is empty, choose it.
    *   *Reasoning:* "Taking a side"

9.  **Fallback (Should not map to a standard game state if priority rules are followed)**
    *   If no priorities trigger (e.g., board is full or invalid state), return the first available empty cell or `(0,0)` if full.
    *   *Reasoning:* "Fallback move"

## Dependencies

*   `fastapi`
*   `uvicorn`
*   `pydantic`

## How to Run

Save the code as `agent.py`, ensure dependencies are installed via `pip install fastapi uvicorn pydantic`, and start the server:

```bash
uvicorn agent:app --host 0.0.0.0 --port 8000
```
