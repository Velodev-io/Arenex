import os
from hashlib import md5
from pathlib import Path

from dotenv import load_dotenv

RUNNER_ROOT = Path(__file__).resolve().parent
REPO_ROOT = RUNNER_ROOT.parent

load_dotenv(RUNNER_ROOT / ".env")


def resolve_runner_path(path_str: str) -> str:
    path = Path(path_str)
    if path.is_absolute():
        return str(path)
    return str((RUNNER_ROOT / path).resolve())

# First bot to collect this many logs wins
WOOD_WIN_CONDITION = int(os.getenv("WOOD_WIN_CONDITION", 64))

# Match time limit in seconds (10 minutes)
MATCH_TIME_LIMIT = int(os.getenv("MATCH_TIME_LIMIT", 600))

# Seconds between /status polls
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", 2.0))

# Seconds to wait for a bot to expose /health
BOT_STARTUP_TIMEOUT = int(os.getenv("BOT_STARTUP_TIMEOUT", 60))

# Bot 1 gets BOT_API_BASE_PORT, Bot 2 gets BOT_API_BASE_PORT + 1
BOT_API_BASE_PORT = int(os.getenv("BOT_API_BASE_PORT", 3001))
VIEWER_PORT_BASE = int(os.getenv("VIEWER_PORT_BASE", 3007))

# Arenex FastAPI backend URL
PLATFORM_API_URL = os.getenv("PLATFORM_API_URL", "http://127.0.0.1:8000")
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "dev-admin-key")

# Minecraft Server connection info
MC_HOST = os.getenv("MC_HOST", "127.0.0.1")
MC_PORT = int(os.getenv("MC_PORT", 25565))

# Host for the 3D viewer (prismarine-viewer)
VIEWER_HOST = os.getenv("VIEWER_HOST", "localhost")

# External tools
NODE_EXECUTABLE = os.getenv("NODE_EXECUTABLE", "/opt/homebrew/bin/node")
BOT_TEMPLATE_PATH = resolve_runner_path(
    os.getenv("BOT_TEMPLATE_PATH", "../minecraft-agent-template/src/index.js")
)


def calculate_viewer_port(match_id: str) -> int:
    slot = int(md5(match_id.encode("utf-8")).hexdigest(), 16) % 100
    return VIEWER_PORT_BASE + (slot * 2)
