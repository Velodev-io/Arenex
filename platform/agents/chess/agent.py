import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chess

app = FastAPI()

# Task 3 requires CORS middleware on all agents so the frontend can call them
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class MoveRequest(BaseModel):
    board: str
    your_mark: str  # Kept consistent with tic-tac-toe agent
    game_id: str = None

def choose_move(board: chess.Board, my_color: chess.Color):
    # Piece Values Guide
    P_VALS = {
        chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
        chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 1000
    }

    # Helper to get piece value
    def piece_value(piece):
        return P_VALS.get(piece.piece_type, 0) if piece else 0

    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None, "No legal moves available"

    # Priority 2: Checkmate opponent if possible
    # (Priority 1: "Don't move into check" is inherently handled by legal_moves)
    for move in legal_moves:
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return move, "Checkmate in one"
        board.pop()

    # Priority 3: Capture highest-value piece safely
    max_net_gain = -float('inf')
    best_capture_move = None
    for move in legal_moves:
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            # En passant capture logic
            if not captured_piece and board.is_en_passant(move):
                captured_piece = chess.Piece(chess.PAWN, not my_color)
                
            if captured_piece:
                gain = piece_value(captured_piece)
                # Check if this square can be recaptured (unsafe)
                board.push(move)
                # If the square is attacked by the opponent, subtract our attacker's value
                if board.is_attacked_by(not my_color, move.to_square):
                    gain -= piece_value(board.piece_at(move.to_square))
                    
                if gain > max_net_gain:
                    max_net_gain = gain
                    best_capture_move = move
                board.pop()
                
    if best_capture_move and max_net_gain > 0:
        return best_capture_move, f"Capturing piece for material gain"

    # Priority 4: Protect hanging pieces
    max_attacked_val = -float('inf')
    best_protect_move = None
    # Find our highest value piece that is attacked
    for square, piece in board.piece_map().items():
        if piece.color == my_color and board.is_attacked_by(not my_color, square):
            pval = piece_value(piece)
            if pval > max_attacked_val:
                # Can we move it to safety?
                for move in legal_moves:
                    if move.from_square == square:
                        board.push(move)
                        # Check if the destination is safe
                        if not board.is_attacked_by(not my_color, move.to_square):
                            max_attacked_val = pval
                            best_protect_move = move
                        board.pop()
                        
    if best_protect_move:
        return best_protect_move, "Protecting piece from capture"

    # Priority 5: Control center squares (e4, d4, e5, d5)
    center_squares = {chess.E4, chess.D4, chess.E5, chess.D5}
    for move in legal_moves:
        if move.to_square in center_squares:
            # Check safety
            board.push(move)
            safe = not board.is_attacked_by(not my_color, move.to_square)
            board.pop()
            if safe:
                return move, "Controlling center square"

    # Priority 6: Develop minor pieces early
    if board.fullmove_number < 10:
        for move in legal_moves:
            piece = board.piece_at(move.from_square)
            if piece and piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                return move, "Developing minor piece in the opening"

    # Priority 7: Castle if available
    # Actually, castling should probably happen before developing ALL pieces, 
    # but strictly following priority check order:
    if board.has_castling_rights(my_color):
        for move in legal_moves:
            if board.is_castling(move):
                return move, "Castling for king safety"

    # Priority 8: Avoid moving same piece twice in opening
    # Since we can't easily track past moves across stateless REST calls without history,
    # we approximate by preferring moves from back-rank starting squares in the opening.
    if board.fullmove_number < 10:
        for move in legal_moves:
            if chess.square_rank(move.from_square) in (0, 7) and not board.piece_type_at(move.from_square) == chess.KING:
                return move, "Preferring undeveloped piece"

    # Priority 9: Any legal move as fallback
    move = random.choice(legal_moves)
    return move, "No strong heuristic applies, choosing randomly"


@app.post("/move")
async def make_move(request: MoveRequest):
    try:
        board = chess.Board(request.board)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid FEN string")

    if board.is_game_over():
        raise HTTPException(status_code=400, detail="Game is over")

    expected_color = chess.WHITE if request.your_mark == "white" else chess.BLACK
    if board.turn != expected_color:
        raise HTTPException(status_code=400, detail="Wrong side to move")

    move, reasoning = choose_move(board, expected_color)
    
    # 1. ILLEGAL MOVES & 2. SELF CHECK Fallback wrapper
    if move not in board.legal_moves:
        legal_list = list(board.legal_moves)
        if legal_list:
            move = legal_list[0]
            reasoning = "Fallback to first legal move due to illegal move selection"
            
    # 3. INFINITE LOOPS IN MIRROR GAMES (Threefold repetition detection)
    if move in board.legal_moves:
        board.push(move)
        if board.is_repetition(3):
            board.pop()
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
