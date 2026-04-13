"""
chess_ai_server.py
------------------
Stockfish-powered chess agent. Uses the same REST contract as the original
rule-based version — identical /move and /health endpoints, same request/response
format. Only the internal decision making changes.
"""

import asyncio
import logging
import os
import random
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional, Tuple

import chess
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from stockfish import Stockfish, StockfishException

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stockfish binary path — use bundled binary in same dir as this file
# ---------------------------------------------------------------------------

_THIS_DIR = Path(__file__).parent
_STOCKFISH_PATH = str((_THIS_DIR / ".." / ".." / "bin" / "stockfish").resolve())

# Stockfish subprocess is NOT thread/async-safe — serialize all calls with a lock
_engine_lock = asyncio.Lock()

STOCKFISH_PARAMS = {
    "Threads": 2,
    "Hash": 256,
    "Move Overhead": 30,
    "Minimum Thinking Time": 200,
    "UCI_LimitStrength": False,
}

_stockfish: Optional[Stockfish] = None

def _create_engine() -> Stockfish:
    """Create a fresh Stockfish engine instance."""
    engine = Stockfish(path=_STOCKFISH_PATH, parameters=STOCKFISH_PARAMS.copy())
    logger.info("Stockfish engine created from %s", _STOCKFISH_PATH)
    return engine

def _get_engine() -> Stockfish:
    """Return the global Stockfish instance, restarting it if it crashed."""
    global _stockfish
    if _stockfish is None:
        _stockfish = _create_engine()
    return _stockfish

def _reset_engine() -> Stockfish:
    """Forcibly restart the Stockfish engine after a crash."""
    global _stockfish
    logger.warning("Restarting Stockfish engine after failure.")
    try:
        if _stockfish is not None:
            _stockfish.__del__()
    except Exception:
        logger.error(e)
    _stockfish = _create_engine()
    return _stockfish

# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    _get_engine()
    logger.info("Chess agent ready — Aggressive Stockfish loaded.")
    yield
    logger.info("Chess agent shutting down.")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="Arenex Chess Agent (Aggressive Stockfish)", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class MoveRequest(BaseModel):
    board: str         # FEN string
    your_color: str    # "white" | "black"
    game_id: str
    difficulty: int = 10  # 1-20 range mapping to aggressive presets

# ---------------------------------------------------------------------------
# Core move-selection logic
# ---------------------------------------------------------------------------

def _get_aggressive_commentary(score: float, fen: str) -> str:
    """Heuristic commentary based on evaluation and board state."""
    board = chess.Board(fen)

    if abs(score) < 0.3:
        return "Maintaining tension in the center — preparing sharp breakthroughs."

    if score > 2.0:
        return "Total domination — dismantling opponent's kingside structure."
    if score < -2.0:
        return "Under pressure but looking for tactical counter-chances."

    # Heuristic for attacks/sacrifices
    comments = [
        "Focusing all pieces on the kingside — looking for a sacrifice.",
        "Aggressive pawn thrust to open lines for the heavy pieces.",
        "Sacrificing positional stability for immediate tactical threats.",
        "Sharp tactical line calculated — forcing weaknesses in the castle.",
        "Exploiting the lack of coordination in opponent's camp."
    ]
    return random.choice(comments)

def _stockfish_move(fen: str, request_difficulty: int) -> Tuple[str, str]:
    """
    Ask Stockfish for the best move with aggressive tuning.
    Also implements Move 1 Opening Book.
    """
    board = chess.Board(fen)

    # --- 1. Opening Book for Sharp Lines (Move 1 Only) ---
    # Move number is indexed by fullness: move 1 white is full_move_number 1, half_moves 0
    if board.fullmove_number == 1:
        if board.turn == chess.WHITE:
            return "e2e4", "Opening Book: King's Pawn (Sharp/Aggressive)"
        else:
            # Black response
            last_move = board.peek() if board.move_stack else None
            # If White played e4, respond with Sicilian (c5)
            if last_move and board.piece_at(last_move.to_square).piece_type == chess.PAWN and last_move.to_square == chess.E4:
                return "c7c5", "Opening Book: Sicilian Defense (Sharp Counter-attack)"
            # If White played d4, respond with King's Indian (Nf6)
            if last_move and board.piece_at(last_move.to_square).piece_type == chess.PAWN and last_move.to_square == chess.D4:
                return "g8f6", "Opening Book: King's Indian Setup (Aggressive/Complex)"

    # --- 2. Difficulty Remap ---
    if request_difficulty <= 5:
        level = 10
        desc = "Easy (Aggressive)"
    elif request_difficulty <= 10:
        level = 15
        desc = "Medium (Aggressive)"
    elif request_difficulty <= 15:
        level = 18
        desc = "Hard (Aggressive)"
    else:
        level = 20
        desc = "Maximum (Aggressive)"

    engine = _get_engine()
    try:
        engine.set_skill_level(level)
        engine.set_fen_position(fen)
        best = engine.get_best_move()
        eval_info = engine.get_evaluation()
    except StockfishException:
        engine = _reset_engine()
        engine.set_skill_level(level)
        engine.set_fen_position(fen)
        best = engine.get_best_move()
        eval_info = engine.get_evaluation()

    if not best:
        raise ValueError("Stockfish returned no move")

    # --- 3. Enhanced Reasoning & Commentary ---
    try:
        if eval_info.get("type") == "cp":
            score = eval_info["value"] / 100.0
            sign = "+" if score >= 0 else ""
            commentary = _get_aggressive_commentary(score, fen)
            reasoning = f"Stockfish eval: {sign}{score:.2f} | {commentary} | Mode: {desc}"
        elif eval_info.get("type") == "mate":
            reasoning = f"MATE IN {abs(eval_info['value'])} | Forcing the final blow! | Mode: {desc}"
        else:
            reasoning = f"Aggressive maneuver found | Mode: {desc}"
    except Exception:
        reasoning = f"Stockfish move (Skill {level})"

    return best, reasoning

def _fallback_move(board: chess.Board) -> str:
    legal = list(board.legal_moves)
    return legal[0].uci() if legal else ""

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/move")
async def make_move(request: MoveRequest):
    try:
        board = chess.Board(request.board)
    except ValueError:
        return {"error": "Invalid FEN string"}, 400

    if board.is_game_over():
        return {"error": "Game is already over"}, 400

    async with _engine_lock:
        try:
            move_uci, reasoning = _stockfish_move(request.board, request.difficulty)
        except Exception as exc:
            logger.error("Stockfish failed (%s); falling back", exc)
            move_uci = _fallback_move(board)
            reasoning = f"Fallback: legal move (Engine logic error)"

    # Safety validation
    try:
        candidate = chess.Move.from_uci(move_uci)
        if candidate not in board.legal_moves:
            raise ValueError("Illegal move")
    except Exception:
        move_uci = _fallback_move(board)
        reasoning = "Fallback: legal move (validation failed)"

    return {"move": move_uci, "reasoning": reasoning}

@app.get("/health")
async def get_health():
    engine = _get_engine()
    try:
        params = engine.get_parameters()
        skill = params.get("Skill Level", 10)
    except Exception:
        skill = -1
    return {"status": "ok", "agent": "aggressive-stockfish", "skill_level": skill}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
