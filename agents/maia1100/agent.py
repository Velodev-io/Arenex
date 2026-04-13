import asyncio
import logging
import os
import subprocess
import signal
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional, Tuple, List, Any

import chess
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_THIS_DIR = Path(__file__).parent
_WEIGHTS_PATH = str(_THIS_DIR / "weights" / "maia-1100.pb.gz")

# Maia uses nodes=1 for pure prediction
UCI_COMMANDS = [
    "uci",
    "setoption name Threads value 2",
    "isready"
]

# ---------------------------------------------------------------------------
# lc0 Subprocess Management
# ---------------------------------------------------------------------------

class LC0Engine:
    def __init__(self, weights_path: str):
        self.weights_path = weights_path
        self.process: Optional[subprocess.Popen] = None
        self.lock = asyncio.Lock()

    def start(self):
        """Start lc0 with Metal backend, falling back to CPU if needed."""
        try:
            logger.info("Initializing lc0 with Metal backend...")
            self.process = subprocess.Popen(
                ["lc0", f"--weights={self.weights_path}", "--backend=metal"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            # Check if it crashed immediately (common if Metal is unavailable)
            import time
            time.sleep(1)
            if self.process.poll() is not None:
                raise RuntimeError("Metal backend failed to start")
            
            self._setup_uci()
            logger.info("lc0 (Metal) initialized successfully.")
        except Exception as e:
            logger.warning(f"Metal engine failed: {e}. Falling back to CPU...")
            self.process = subprocess.Popen(
                ["lc0", f"--weights={self.weights_path}", "--backend=blas"], # BLAS is common for CPU
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            self._setup_uci()
            logger.info("lc0 (CPU) initialized successfully.")

    def _setup_uci(self):
        """Initialize UCI state."""
        self._send("uci")
        self._wait_for("uciok")
        self._send("setoption name Threads value 2")
        self._send("isready")
        self._wait_for("readyok")

    def _send(self, cmd: str):
        if self.process and self.process.stdin:
            self.process.stdin.write(f"{cmd}\n")
            self.process.stdin.flush()

    def _wait_for(self, token: str, timeout: float = 5.0):
        if not self.process or not self.process.stdout:
            return
        
        # Note: This is a blocking read in a setup phase, acceptable once at startup
        while True:
            line = self.process.stdout.readline().strip()
            if token in line:
                break

    async def get_move(self, fen: str) -> str:
        async with self.lock:
            if not self.process or self.process.poll() is not None:
                self.start()

            self._send(f"position fen {fen}")
            self._send("go nodes 1")
            
            # Non-blocking read loop
            while True:
                line = await asyncio.to_thread(self.process.stdout.readline)
                line = line.strip()
                if line.startswith("bestmove"):
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1]
                    break
            return ""

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None

_engine = LC0Engine(_WEIGHTS_PATH)

# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    _engine.start()
    yield
    _engine.stop()

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="Maia-1100 Chess Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MoveRequest(BaseModel):
    board: str
    your_color: Optional[str] = None # Platform standard
    your_mark: Optional[str] = None  # Maia request standard
    game_id: Optional[str] = None

@app.post("/move")
async def make_move(request: MoveRequest):
    try:
        board = chess.Board(request.board)
    except Exception:
        return {"error": "Invalid FEN"}, 400

    if board.is_game_over():
        return {"error": "Game over"}, 400

    try:
        # 10s timeout for move calculation
        move_uci = await asyncio.wait_for(_engine.get_move(request.board), timeout=10.0)
    except Exception as e:
        logger.error(f"lc0 error: {e}")
        # Fallback to first legal move
        legal_moves = list(board.legal_moves)
        move_uci = legal_moves[0].uci() if legal_moves else ""

    return {
        "move": move_uci,
        "reasoning": "Maia-1100 prediction (nodes 1)"
    }

@app.get("/health")
async def get_health():
    return {
        "status": "ok",
        "agent": "maia-1100",
        "elo": 1100
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
