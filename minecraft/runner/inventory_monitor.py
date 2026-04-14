import asyncio
import httpx
import logging
import time
from typing import Dict, Optional, List
from bot_process import BotProcess
from config import WOOD_WIN_CONDITION

logger = logging.getLogger(__name__)

class InventoryMonitor:
    def __init__(self, bot1: BotProcess, bot2: Optional[BotProcess] = None):
        self.bot1 = bot1
        self.bot2 = bot2
        self.consecutive_failures = {bot1.bot_name: 0}
        if bot2:
            self.consecutive_failures[bot2.bot_name] = 0

    def normalize_status(self, bot: BotProcess, status: dict) -> dict:
        wood_count = status.get("wood_count")
        if wood_count is None:
            wood_count = status.get("wood_collected", 0)

        position = status.get("position")
        if not isinstance(position, dict):
            position = None

        current_action = status.get("current_action")
        if not current_action:
            current_action = "idle" if status.get("alive", status.get("connected", False)) else "offline"

        return {
            **status,
            "name": status.get("name") or status.get("bot") or bot.bot_name,
            "wood_count": wood_count,
            "health": status.get("health", 0),
            "current_action": current_action,
            "position": position,
            "connected": status.get("connected", status.get("alive", False)),
        }
    
    async def get_status(self, bot: BotProcess) -> Optional[dict]:
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                resp = await client.get(f"{bot.api_url}/status")
                if resp.status_code == 200:
                    self.consecutive_failures[bot.bot_name] = 0
                    return self.normalize_status(bot, resp.json())
        except Exception as e:
            logger.warning(f"Poll fail for {bot.bot_name}: {e}")
        
        self.consecutive_failures[bot.bot_name] += 1
        return None

    async def poll_once(self) -> dict:
        calls = [self.get_status(self.bot1)]
        if self.bot2:
            calls.append(self.get_status(self.bot2))
        
        results = await asyncio.gather(*calls)
        
        return {
            "bot1": results[0],
            "bot2": results[1] if self.bot2 else None,
            "timestamp": int(time.time())
        }
    
    async def check_win_condition(self, poll_result: dict) -> Optional[str]:
        # bot1/bot2 in poll_result match self.bot1/self.bot2
        status1 = poll_result["bot1"]
        status2 = poll_result["bot2"]
        
        # Check for wood collection win
        wood1 = status1.get("wood_count", 0) if status1 else 0
        wood2 = status2.get("wood_count", 0) if status2 else 0
        
        # Check for forfeit (3 fails)
        if self.consecutive_failures[self.bot1.bot_name] >= 3:
            logger.info(f"{self.bot1.bot_name} forfeited due to connectivity.")
            return "bot2" if self.bot2 else "draw"
        if self.bot2 and self.consecutive_failures[self.bot2.bot_name] >= 3:
            logger.info(f"{self.bot2.bot_name} forfeited due to connectivity.")
            return "bot1"

        # Win condition logic
        bot1_wins = wood1 >= WOOD_WIN_CONDITION
        bot2_wins = wood2 >= WOOD_WIN_CONDITION
        
        if bot1_wins and bot2_wins:
            return "draw"
        if bot1_wins:
            return "bot1"
        if bot2_wins:
            return "bot2"
            
        return None
