import os
from hashlib import md5
from dotenv import load_dotenv

load_dotenv()

# First bot to collect this many logs wins
WOOD_WIN_CONDITION = int(os.getenv("WOOD_WIN_CONDITION", 64))

# Match time limit in seconds (10 minutes)
MATCH_TIME_LIMIT = int(os.getenv("MATCH_TIME_LIMIT", 600))

# Seconds between /status polls
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", 2.0))

# Seconds to wait for bot to come online
BOT_STARTUP_TIMEOUT = int(os.getenv("BOT_STARTUP_TIMEOUT", 30))

# Bot 1 gets BOT_API_BASE_PORT, Bot 2 gets BOT_API_BASE_PORT + 1
BOT_API_BASE_PORT = int(os.getenv("BOT_API_BASE_PORT", 3001))
VIEWER_PORT_BASE = int(os.getenv("VIEWER_PORT_BASE", 3007))

# Arenex FastAPI backend URL
PLATFORM_API_URL = os.getenv("PLATFORM_API_URL", "http://localhost:8000")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "dev-admin-key")

# Minecraft Server connection info
MC_HOST = os.getenv("MC_HOST", "localhost")
MC_PORT = int(os.getenv("MC_PORT", 25565))

# External tools
NODE_EXECUTABLE = os.getenv("NODE_EXECUTABLE", "/opt/homebrew/bin/node")
BOT_TEMPLATE_PATH = os.getenv("BOT_TEMPLATE_PATH", "../minecraft-agent-template/src/index.js")


def calculate_viewer_port(match_id: str) -> int:
    slot = int(md5(match_id.encode("utf-8")).hexdigest(), 16) % 100
    return VIEWER_PORT_BASE + (slot * 2)
