import chess
from datetime import datetime, timezone

class ChessHandler:
    @staticmethod
    def initialize_board():
        board = chess.Board()
        board.remove_piece_at(chess.A2)
        board.remove_piece_at(chess.A7)
        return board

    @staticmethod
    def get_payload(board, turn, match_id):
        return {
            "board": board.fen(),
            "your_color": turn,
            "game_id": str(match_id),
            "difficulty": 10
        }

    @staticmethod
    def process_move(board, turn, data):
        move_uci = data.get("move")
        if not move_uci:
            raise ValueError("Missing 'move' in response")
        move = chess.Move.from_uci(move_uci)
        if move not in board.legal_moves:
            raise ValueError("Illegal move")
        board.push(move)
        return {
            "agent": turn,
            "move": move_uci,
            "fen": board.fen(),
            "reasoning": data.get("reasoning", ""),
            "timestamp": str(datetime.now(timezone.utc))
        }

    @staticmethod
    def check_result(board, turn):
        if board.is_checkmate():
            return "finished", "white_wins" if turn == "white" else "black_wins"
        if board.is_game_over():
            return "finished", "draw"
        return "live", None
