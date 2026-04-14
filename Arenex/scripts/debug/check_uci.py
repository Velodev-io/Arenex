from stockfish import Stockfish
from pathlib import Path

_THIS_DIR = Path("ChessAgent")
_STOCKFISH_PATH = str(_THIS_DIR / "bin" / "stockfish")

try:
    engine = Stockfish(path=_STOCKFISH_PATH)
    logger.info("Available Options:")
    # There isn't a direct 'get_available_options' in the lib, 
    # but we can try setting them or checking the binary via shell
except Exception as e:
    logger.info(f"Error: {e}")
