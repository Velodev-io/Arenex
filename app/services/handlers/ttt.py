from datetime import datetime, timezone

class TTTHandler:
    @staticmethod
    def initialize_board():
        return [["","",""],["","",""],["","",""]]

    @staticmethod
    def get_payload(board, turn, match_id):
        return {
            "board": board,
            "your_mark": "X" if turn == "white" else "O",
            "game_id": str(match_id)
        }

    @staticmethod
    def process_move(board, turn, data):
        r, c = data.get("row"), data.get("col")
        if r is None or c is None or r < 0 or r > 2 or c < 0 or c > 2 or board[r][c] != "":
            raise ValueError("Illegal cell selection")
        mark = "X" if turn == "white" else "O"
        board[r][c] = mark
        return {
            "agent": turn,
            "move": {"row": r, "col": c},
            "board": [row[:] for row in board],
            "reasoning": data.get("reasoning", ""),
            "timestamp": str(datetime.now(timezone.utc))
        }

    @staticmethod
    def check_result(board, turn):
        mark = "X" if turn == "white" else "O"
        if TTTHandler._check_winner(board, mark):
            return "finished", "white_wins" if turn == "white" else "black_wins"
        if TTTHandler._is_full(board):
            return "finished", "draw"
        return "live", None

    @staticmethod
    def _check_winner(board, mark):
        lines = [
            [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
            [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
            [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)],
        ]
        for line in lines:
            if all(board[r][c] == mark for r, c in line):
                return True
        return False

    @staticmethod
    def _is_full(board):
        return all(board[r][c] != "" for r in range(3) for c in range(3))
