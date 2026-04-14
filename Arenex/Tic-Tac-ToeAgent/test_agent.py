import requests
import json

BASE = "http://localhost:8000"

def print_board(board):
    symbols = {"X": "X", "O": "O", "": "."}
    for row in board:
        logger.info(" | ".join(symbols[c] for c in row))
        logger.info("-" * 9)
    logger.info()

def test(label, board, mark):
    res = requests.post(f"{BASE}/move", json={
        "board": board,
        "your_mark": mark,
        "game_id": "test"
    })
    data = res.json()
    logger.info(f"Test: {label}")
    print_board(board)
    logger.info(f"Move: row={data['row']}, col={data['col']}")
    logger.info(f"Reasoning: {data['reasoning']}\n")

# Test 1: Agent should take the win
test(
    "Take the win (row 0)",
    board=[["X","X",""], ["O","O","X"], ["","","O"]],
    mark="X"
)

# Test 2: Agent should block opponent
test(
    "Block opponent win (col 2)",
    board=[["O","X",""], ["X","O",""], ["X","",""]],
    mark="X"
)

# Test 3: Agent should take center
test(
    "Take center",
    board=[["X","",""], ["","",""], ["","","O"]],
    mark="O"
)

# Test 4: Empty board — should take center or corner
test(
    "Empty board",
    board=[["","",""], ["","",""], ["","",""]],
    mark="X"
)
