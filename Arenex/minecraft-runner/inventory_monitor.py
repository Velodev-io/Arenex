import asyncio
import httpx
import logging
import time
from typing import Dict, Optional, List
from bot_process import BotProcess
from config import WOOD_WIN_CONDITION

logger = logging.getLogger(__name__)

class InventoryMonitor:
    def __init__(self, bot1: BotProcess, bot2: BotProcess):
        self.bot1 = bot1
        self.bot2 = bot2
        self.consecutive_failures = {bot1.bot_name: 0, bot2.bot_name: 0}
    
    async def get_status(self, bot: BotProcess) -> Optional[dict]:
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                resp = await client.get(f"{bot.api_url}/status")
                if resp.status_code == 200:
                    self.consecutive_failures[bot.bot_name] = 0
                    return resp.json()
        except Exception as e:
            logger.warning(f"Poll fail for {bot.bot_name}: {e}")
        
        self.consecutive_failures[bot.bot_name] += 1
        return None

    async def poll_once(self) -> dict:
        results = await asyncio.gather(
            self.get_status(self.bot1),
            self.get_status(self.bot2)
        )
        
        return {
            "bot1": results[0],
            "bot2": results[1],
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
            return "bot2"
        if self.consecutive_failures[self.bot2.bot_name] >= 3:
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
