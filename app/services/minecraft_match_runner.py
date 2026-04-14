import asyncio
import logging
import os
import sys
from pathlib import Path

from sqlalchemy.future import select

from app.database import AsyncSessionLocal
from app.models import Agent, Match

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = REPO_ROOT / "minecraft" / "runner" / "match_runner.py"
RUNNER_LOG_PATH = REPO_ROOT / "logs" / "match_runner.log"
DEFAULT_BOT_SCRIPT_PATH = REPO_ROOT / "minecraft" / "agent-template" / "src" / "index.js"


def resolve_bot_script_path(script_path: str | None) -> str:
    if script_path:
        path = Path(script_path).expanduser()
        if not path.is_absolute():
            repo_relative = (REPO_ROOT / path).resolve()
            runner_relative = (RUNNER_PATH.parent / path).resolve()
            if repo_relative.exists():
                return str(repo_relative)
            if runner_relative.exists():
                return str(runner_relative)
            return str(repo_relative)
        return str(path)

    return str(DEFAULT_BOT_SCRIPT_PATH)


def build_minecraft_runner_command(match_id: int, bot1: Agent, bot2: Agent) -> list[str]:
    command = [
        sys.executable,
        str(RUNNER_PATH),
        "--match-id",
        str(match_id),
        "--bot1-name",
        bot1.name,
        "--bot2-name",
        bot2.name,
        "--bot1-agent-id",
        str(bot1.id),
        "--bot2-agent-id",
        str(bot2.id),
    ]

    bot1_script = resolve_bot_script_path(os.getenv("MINECRAFT_BOT1_SCRIPT") or os.getenv("MINECRAFT_BOT_SCRIPT"))
    bot2_script = resolve_bot_script_path(os.getenv("MINECRAFT_BOT2_SCRIPT") or os.getenv("MINECRAFT_BOT_SCRIPT"))

    command.extend(["--bot1-script", bot1_script])
    command.extend(["--bot2-script", bot2_script])

    return command


async def run_minecraft_match(match_id: int) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Match).where(Match.id == match_id))
        match = result.scalars().first()
        if not match or match.is_practice:
            logger.warning("Skipping Minecraft runner launch for invalid match %s.", match_id)
            return

        res_w = await db.execute(select(Agent).where(Agent.id == match.agent_white_id))
        bot1 = res_w.scalars().first()
        res_b = await db.execute(select(Agent).where(Agent.id == match.agent_black_id))
        bot2 = res_b.scalars().first()

        if not bot1 or not bot2:
            logger.error("Minecraft match %s is missing one or both agents.", match_id)
            return

        if bot1.game_type != "minecraft_wood_race" or bot2.game_type != "minecraft_wood_race":
            logger.warning(
                "Minecraft runner called for non-Minecraft agents in match %s: %s vs %s",
                match_id,
                bot1.game_type,
                bot2.game_type,
            )
            return

    command = build_minecraft_runner_command(match_id, bot1, bot2)
    logger.info("Launching Minecraft runner for match %s: %s", match_id, command)

    RUNNER_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RUNNER_LOG_PATH.open("ab") as runner_log:
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=str(REPO_ROOT),
            stdout=runner_log,
            stderr=runner_log,
        )

    logger.info(
        "Minecraft runner started for match %s with pid %s. Logs: %s",
        match_id,
        process.pid,
        RUNNER_LOG_PATH,
    )
