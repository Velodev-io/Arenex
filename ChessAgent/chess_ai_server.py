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
_STOCKFISH_PATH = str(_THIS_DIR / "bin" / "stockfish")

# Stockfish subprocess is NOT thread/async-safe — serialize all calls with a lock
_engine_lock = asyncio.Lock()

STOCKFISH_PARAMS = {
    "Threads": 2,
    "Minimum Thinking Time": 100,
    "Skill Level": 10,
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
        pass
    _stockfish = _create_engine()
    return _stockfish


# ---------------------------------------------------------------------------
# Lifespan: warm up the engine at startup so the first request isn't slow
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    _get_engine()
    logger.info("Chess agent ready — Stockfish loaded.")
    yield
    logger.info("Chess agent shutting down.")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="Arenex Chess Agent (Stockfish)", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request / Response models (identical contract to previous agent)
# ---------------------------------------------------------------------------

class MoveRequest(BaseModel):
    board: str         # FEN string
    your_color: str    # "white" | "black"
    game_id: str
    difficulty: int = 10  # 1-20 Stockfish skill level; default = medium


# ---------------------------------------------------------------------------
# Core move-selection logic
# ---------------------------------------------------------------------------

def _fallback_move(board: chess.Board) -> str:
    """Return the first legal UCI move. Never raises."""
    legal = list(board.legal_moves)
    return legal[0].uci() if legal else ""


def _stockfish_move(fen: str, skill_level: int) -> Tuple[str, str]:
    """
    Ask Stockfish for the best move and evaluation.

    Returns (uci_move, reasoning_string).
    Raises on unrecoverable failure — caller must handle.
    """
    engine = _get_engine()

    # Clamp skill level
    level = max(1, min(20, skill_level))
    try:
        engine.set_skill_level(level)
        engine.set_fen_position(fen)
        best = engine.get_best_move()
    except StockfishException:
        # Engine died — restart it and try ONE more time
        engine = _reset_engine()
        engine.set_skill_level(level)
        engine.set_fen_position(fen)
        best = engine.get_best_move()

    if not best:
        raise ValueError("Stockfish returned no move")

    # Evaluation string for reasoning
    try:
        eval_info = engine.get_evaluation()
        if eval_info.get("type") == "cp":
            score = eval_info["value"] / 100.0
            sign = "+" if score >= 0 else ""
            reasoning = f"Stockfish eval: {sign}{score:.2f} (skill {level}/20)"
        elif eval_info.get("type") == "mate":
            reasoning = f"Stockfish: Mate in {eval_info['value']} (skill {level}/20)"
        else:
            reasoning = f"Stockfish move (skill {level}/20)"
    except Exception:
        reasoning = f"Stockfish move (skill {level}/20)"

    return best, reasoning


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

    move_uci: str = ""
    reasoning: str = ""

    # --- Primary: Stockfish (lock prevents concurrent subprocess corruption) ---
    async with _engine_lock:
        try:
            move_uci, reasoning = _stockfish_move(request.board, request.difficulty)
        except (StockfishException, ValueError, Exception) as exc:
            logger.error("Stockfish failed (%s); falling back to first legal move", exc)
            move_uci = _fallback_move(board)
            reasoning = f"Fallback: first legal move (Stockfish error: {type(exc).__name__})"

    # --- Safety net: ensure the move is strictly legal ---
    try:
        candidate = chess.Move.from_uci(move_uci)
        if candidate not in board.legal_moves:
            raise ValueError("Illegal move returned by engine")
    except Exception as exc:
        logger.error("Move validation failed (%s); using fallback.", exc)
        move_uci = _fallback_move(board)
        reasoning = "Fallback: first legal move (move failed validation)"

    if not move_uci:
        return {"error": "No legal moves available"}, 400

    return {"move": move_uci, "reasoning": reasoning}


@app.get("/health")
async def get_health():
    engine = _get_engine()
    # Read current skill level from engine parameters
    try:
        params = engine.get_parameters()
        skill = params.get("Skill Level", 10)
    except Exception:
        skill = STOCKFISH_PARAMS["Skill Level"]

    return {"status": "ok", "agent": "chess-agent-stockfish", "skill_level": skill}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)