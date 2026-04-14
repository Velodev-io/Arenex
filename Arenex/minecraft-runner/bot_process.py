import os
import asyncio
import httpx
import logging
import signal
from typing import Optional
from config import NODE_EXECUTABLE, BOT_STARTUP_TIMEOUT, MC_HOST, MC_PORT

logger = logging.getLogger(__name__)

class BotProcess:
    def __init__(self, bot_name: str, api_port: int, match_id: str, bot_script_path: str, viewer_port: int = 0):
        self.bot_name = bot_name
        self.api_port = api_port
        self.match_id = match_id
        self.bot_script_path = bot_script_path
        self.viewer_port = viewer_port
        self.process: Optional[asyncio.subprocess.Process] = None
    
    @property
    def api_url(self) -> str:
        return f"http://localhost:{self.api_port}"

    def build_env(self) -> dict:
        env = os.environ.copy()
        env.update({
            "BOT_NAME": self.bot_name,
            "MC_HOST": MC_HOST,
            "MC_PORT": str(MC_PORT),
            "API_PORT": str(self.api_port),
            "MATCH_ID": self.match_id,
            "VIEWER_PORT": str(self.viewer_port),
        })
        return env

    async def start(self) -> bool:
        env = self.build_env()

        logger.info(f"Starting bot {self.bot_name} on port {self.api_port}...")
        
        try:
            self.process = await asyncio.create_subprocess_exec(
                NODE_EXECUTABLE,
                self.bot_script_path,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
        except Exception as e:
            logger.error(f"Failed to spawn node process: {e}")
            return False

        # Wait for /health to respond
        start_time = asyncio.get_event_loop().time()
        async with httpx.AsyncClient() as client:
            while (asyncio.get_event_loop().time() - start_time) < BOT_STARTUP_TIMEOUT:
                try:
                    resp = await client.get(f"{self.api_url}/health")
                    if resp.status_code == 200:
                        logger.info(f"Bot {self.bot_name} is alive.")
                        return True
                except (httpx.ConnectError, httpx.RequestError):
                    pass
                await asyncio.sleep(1.0)
        
        logger.error(f"Bot {self.bot_name} failed to become healthy within {BOT_STARTUP_TIMEOUT}s")
        await self.stop()
        return False

    async def stop(self):
        if not self.process:
            return

        logger.info(f"Stopping bot {self.bot_name}...")
        
        # 1. Try /stop endpoint
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                await client.post(f"{self.api_url}/stop")
            # Wait for clean exit
            for _ in range(3):
                if self.process.returncode is not None:
                    return
                await asyncio.sleep(1.0)
        except Exception as e:
            logger.warning(f"Failed to stop bot via API: {e}")

        # 2. SIGTERM
        if self.process.returncode is None:
            logger.info(f"Killing bot {self.bot_name} with SIGTERM...")
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=2.0)
                return
            except asyncio.TimeoutError:
                pass

        # 3. SIGKILL
        if self.process.returncode is None:
            logger.info(f"Killing bot {self.bot_name} with SIGKILL...")
            self.process.kill()
            await self.process.wait()

    async def is_alive(self) -> bool:
        if not self.process or self.process.returncode is not None:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                resp = await client.get(f"{self.api_url}/health")
                return resp.status_code == 200
        except Exception:
            return False
