from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request / Response Contract ---

class GameState(BaseModel):
    board: List[List[str]]   # 3x3 grid, "" = empty, "X" or "O"
    your_mark: str            # "X" or "O"
    game_id: Optional[str] = None

class MoveResponse(BaseModel):
    row: int
    col: int
    reasoning: str

# --- Core Logic ---

def get_empty_cells(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] == ""]

def check_winner(board, mark):
    lines = [
        # rows
        [(0,0),(0,1),(0,2)],
        [(1,0),(1,1),(1,2)],
        [(2,0),(2,1),(2,2)],
        # cols
        [(0,0),(1,0),(2,0)],
        [(0,1),(1,1),(2,1)],
        [(0,2),(1,2),(2,2)],
        # diagonals
        [(0,0),(1,1),(2,2)],
        [(0,2),(1,1),(2,0)],
    ]
    for line in lines:
        if all(board[r][c] == mark for r, c in line):
            return True
    return False

def find_winning_move(board, mark):
    """Find a move that wins the game for `mark`."""
    for r, c in get_empty_cells(board):
        board[r][c] = mark
        if check_winner(board, mark):
            board[r][c] = ""
            return (r, c)
        board[r][c] = ""
    return None

def find_fork(board, mark):
    """Find a move that creates two winning threats."""
    for r, c in get_empty_cells(board):
        board[r][c] = mark
        winning_threats = 0
        for r2, c2 in get_empty_cells(board):
            board[r2][c2] = mark
            if check_winner(board, mark):
                winning_threats += 1
            board[r2][c2] = ""
        board[r][c] = ""
        if winning_threats >= 2:
            return (r, c)
    return None

def choose_move(board, my_mark):
    opponent = "O" if my_mark == "X" else "X"

    # Priority 1: Win immediately
    move = find_winning_move(board, my_mark)
    if move:
        return move, "Taking the win"

    # Priority 2: Block opponent's winning move
    move = find_winning_move(board, opponent)
    if move:
        return move, "Blocking opponent's win"

    # Priority 3: Create a fork (two winning threats)
    move = find_fork(board, my_mark)
    if move:
        return move, "Creating a fork"

    # Priority 4: Block opponent's fork
    move = find_fork(board, opponent)
    if move:
        return move, "Blocking opponent's fork"

    # Priority 5: Take center
    if board[1][1] == "":
        return (1, 1), "Taking center"

    # Priority 6: Take opposite corner from opponent
    corners = [(0,0),(0,2),(2,0),(2,2)]
    opposites = {(0,0):(2,2), (0,2):(2,0), (2,0):(0,2), (2,2):(0,0)}
    for r, c in corners:
        if board[r][c] == opponent:
            opp = opposites[(r, c)]
            if board[opp[0]][opp[1]] == "":
                return opp, "Taking opposite corner"

    # Priority 7: Take any empty corner
    for r, c in corners:
        if board[r][c] == "":
            return (r, c), "Taking a corner"

    # Priority 8: Take any empty side
    sides = [(0,1),(1,0),(1,2),(2,1)]
    for r, c in sides:
        if board[r][c] == "":
            return (r, c), "Taking a side"

    return None, "No moves available"

# --- API Endpoint ---

@app.post("/move", response_model=MoveResponse)
def make_move(state: GameState):
    board = [row[:] for row in state.board]  # copy to avoid mutation
    move, reasoning = choose_move(board, state.your_mark)

    if move is None:
        # Fallback: should not happen in a valid game
        empty = get_empty_cells(board)
        move = empty[0] if empty else (0, 0)
        reasoning = "Fallback move"

    return MoveResponse(row=move[0], col=move[1], reasoning=reasoning)

@app.get("/health")
def health():
    return {"status": "ok", "agent": "rule-based-tictactoe"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
