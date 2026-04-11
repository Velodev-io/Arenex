from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chess
import random

app = FastAPI()

class MoveRequest(BaseModel):
    board: str
    your_color: str
    game_id: str

def choose_move(board: chess.Board):
    # Priority 1: Don't move into check (already handled by legal_moves)
    
    # Priority 2: Checkmate opponent if possible
    for move in board.legal_moves:
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return move, "Checkmate in one"
        board.pop()

    # Priority 3: Check opponent (if it leads to a winning position safely)
    for move in board.legal_moves:
        board.push(move)
        if board.is_check():
            board.pop()
            return move, "Delivering check to gain tempo"
        board.pop()

    # Priority 4: Capture the highest-value piece safely
    max_net_gain = -float('inf')
    best_move = None
    for move in board.legal_moves:
        board.push(move)
        net_gain = 0
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                piece_type = captured_piece.piece_type
                if piece_type == chess.PAWN:
                    net_gain += 1
                elif piece_type == chess.KNIGHT:
                    net_gain += 3
                elif piece_type == chess.BISHOP:
                    net_gain += 3
                elif piece_type == chess.ROOK:
                    net_gain += 5
                elif piece_type == chess.QUEEN:
                    net_gain += 9
        if net_gain > max_net_gain:
            max_net_gain = net_gain
            best_move = move
        board.pop()
    if best_move:
        return best_move, f"Capturing {chess.PIECE_NAMES[board.piece_at(best_move.to_square).piece_type]} for material gain (+{max_net_gain})"

    # Priority 5: Protect own pieces under attack
    max_piece_value = -float('inf')
    best_move = None
    for move in board.legal_moves:
        board.push(move)
        for square in board.attacked_squares:
            piece = board.piece_at(square)
            if piece and piece.color == board.turn:
                piece_type = piece.piece_type
                if piece_type == chess.PAWN:
                    piece_value = 1
                elif piece_type == chess.KNIGHT:
                    piece_value = 3
                elif piece_type == chess.BISHOP:
                    piece_value = 3
                elif piece_type == chess.ROOK:
                    piece_value = 5
                elif piece_type == chess.QUEEN:
                    piece_value = 9
                if piece_value > max_piece_value:
                    max_piece_value = piece_value
                    best_move = move
        board.pop()
    if best_move:
        return best_move, f"Protecting {chess.PIECE_NAMES[board.piece_at(best_move.to_square).piece_type]} from capture"

    # Priority 6: Control center squares
    center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
    for move in board.legal_moves:
        if move.to_square in center_squares:
            return move, f"Controlling center square {chess.square_name(move.to_square)}"

    # Priority 7: Develop pieces early
    if board.fullmove_number < 10:
        for move in board.legal_moves:
            piece = board.piece_at(move.from_square)
            if piece and piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                return move, f"Developing {chess.PIECE_NAMES[piece.piece_type]} in the opening"

    # Priority 8: Castle if possible
    if board.has_kingside_castling_rights(board.turn):
        for move in board.legal_moves:
            if move.from_square == chess.E1 and move.to_square == chess.G1:
                return move, "Castling for king safety"
    if board.has_queenside_castling_rights(board.turn):
        for move in board.legal_moves:
            if move.from_square == chess.E1 and move.to_square == chess.C1:
                return move, "Castling for king safety"

    # Priority 9: Avoid moving the same piece twice in the opening
    if board.fullmove_number < 10:
        moved_pieces = set()
        for move in board.legal_moves:
            piece = board.piece_at(move.from_square)
            if piece and move.from_square not in moved_pieces:
                moved_pieces.add(move.from_square)
                return move, "Preferring undeveloped piece"

    # Priority 10: Fall back to a random legal move
    move = random.choice(list(board.legal_moves))
    return move, "No strong heuristic applies, choosing randomly"

@app.post("/move")
async def make_move(request: MoveRequest):
    try:
        board = chess.Board(request.board)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid FEN string")
    if board.is_game_over():
        raise HTTPException(status_code=400, detail="Game is over")
    if (board.turn == chess.WHITE and request.your_color != "white") or (board.turn == chess.BLACK and request.your_color != "black"):
        raise HTTPException(status_code=400, detail="Wrong side to move")
    
    move, reasoning = choose_move(board)
    
    # 1. ILLEGAL MOVES & 2. SELF CHECK
    # Ensure the move is strictly legal; if not, fall back
    if move not in board.legal_moves:
        legal_list = list(board.legal_moves)
        if legal_list:
            move = legal_list[0]
            reasoning = "Fallback to first legal move due to illegal move selection"

    # 3. INFINITE LOOPS IN MIRROR GAMES
    # Check for threefold repetition
    if move in board.legal_moves:
        board.push(move)
        if board.is_repetition(3):
            board.pop()
            # Try to find a move that avoids repetition
            for alt_move in list(board.legal_moves):
                board.push(alt_move)
                if not board.is_repetition(3):
                    move = alt_move
                    reasoning = "Avoiding threefold repetition"
                    board.pop()
                    break
                board.pop()
        else:
            board.pop()

    return {"move": move.uci(), "reasoning": reasoning}

@app.get("/health")
async def get_health():
    return {"status": "ok", "agent": "chess-agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)