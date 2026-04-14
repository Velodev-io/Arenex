# Tic-Tac-Toe Tester Agent Spec

## Overview
This file contains integration tests for the Tic-Tac-Toe agent. It verifies that the agent respects the priority rules defined in its strategy by evaluating its responses to specific predefined board states.

## How it Works (Logic & Flow)
1.  **Setup Target:** It targets the local agent server at `http://localhost:8000`.
2.  **Define Test Helper:** It includes a `test(label, board, mark)` function that:
    *   Sends a `POST /move` request to the agent server with the given `board` and player `mark`.
    *   Prints a human-readable visualization of the board to the console.
    *   Extracts and prints the selected `row`, `col`, and `reasoning` from the JSON response.
3.  **Run Scenarios:** It sequentially executes 4 specific board scenarios:
    *   **Test 1: Take the win.** Board has a winning opportunity for `X` in the top row. The test expects the agent to select the winning cell.
    *   **Test 2: Block opponent.** Board has a winning opportunity for `O` in the right column. The test (playing as `X`) expects the agent to block that column.
    *   **Test 3: Take center.** Board is nearly empty, but `O` is in a corner. The test expects the agent to prioritize taking the center cell.
    *   **Test 4: Empty board.** A completely empty board. The test expects the agent to prioritize an empty piece based on its logic (typically the center or a corner).

## Request Format
The tester sends standard Arena JSON payloads via HTTP POST:
```json
{
  "board": [["X","X",""], ["O","O","X"], ["","","O"]],
  "your_mark": "X",
  "game_id": "test"
}
```

## Dependencies
*   `requests`
*   `json` (built-in)

## How to Run
Ensure the Tic-Tac-Toe agent server is running on port 8000. Then execute the script directly:

```bash
python test_agent.py
```
This will print out the board state and the agent's decision for each of the 4 scenarios.
