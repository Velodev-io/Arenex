import asyncio
import httpx
import json
import logging
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, urlunparse
from config import PLATFORM_API_URL, ADMIN_API_KEY

logger = logging.getLogger(__name__)


def platform_api_candidates() -> list[str]:
    candidates = [PLATFORM_API_URL.rstrip("/")]
    parsed = urlparse(candidates[0])

    alternate_host = None
    if parsed.hostname == "localhost":
        alternate_host = "127.0.0.1"
    elif parsed.hostname == "127.0.0.1":
        alternate_host = "localhost"

    if alternate_host:
        netloc = alternate_host
        if parsed.port:
            netloc = f"{alternate_host}:{parsed.port}"
        alternate = urlunparse(parsed._replace(netloc=netloc)).rstrip("/")
        if alternate not in candidates:
            candidates.append(alternate)

    return candidates


async def post_with_retries(path: str, *, json_payload: dict, headers: dict | None = None) -> httpx.Response | None:
    headers = headers or {}

    for base_url in platform_api_candidates():
        for attempt in range(1, 4):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(f"{base_url}{path}", json=json_payload, headers=headers)
                    return response
            except Exception as exc:
                logger.warning(
                    "POST %s%s failed on attempt %s: %r",
                    base_url,
                    path,
                    attempt,
                    exc,
                )
                if attempt < 3:
                    await asyncio.sleep(0.5 * attempt)

    return None


async def mark_live_viewer(match_id: str) -> bool:
    resp = await post_with_retries(
        f"/matches/{match_id}/live-viewer",
        json_payload={"had_live_viewer": True},
        headers={"x-admin-api-key": ADMIN_API_KEY},
    )
    if resp is None:
        logger.error("Failed to mark live viewer for match %s after retries.", match_id)
        return False

    if resp.status_code == 204:
        logger.info("Marked match %s as having a live viewer.", match_id)
        return True

    logger.error("Platform rejected live-viewer update (%s): %s", resp.status_code, resp.text)

    return False

async def report_result(
    match_id: str,
    winner: str,           # "bot1", "bot2", or "draw"
    bot1_name: str,
    bot2_name: str,
    bot1_agent_id: str,
    bot2_agent_id: str,
    duration_seconds: int,
    final_wood_bot1: int,
    final_wood_bot2: int,
    reason: str,           # "wood_collected", "opponent_forfeit", "time_limit"
    timeline: list = None
) -> bool:
    
    # ... code to determine winner omitted for brevity in instruction if needed, but I'll provide full replacement ...
    winner_agent_id = None
    loser_agent_id = None
    result_type = "win"

    if winner == "bot1":
        winner_agent_id = bot1_agent_id
        loser_agent_id = bot2_agent_id
    elif winner == "bot2":
        winner_agent_id = bot2_agent_id
        loser_agent_id = bot1_agent_id
    else:
        winner_agent_id = bot1_agent_id
        loser_agent_id = bot2_agent_id
        result_type = "draw"

    payload = {
        "match_id": match_id,
        "game_type": "minecraft_wood_race",
        "winner_agent_id": winner_agent_id,
        "loser_agent_id": loser_agent_id,
        "result": result_type,
        "duration_seconds": duration_seconds,
        "timeline": timeline or [],
        "metadata": {
            "bot1_wood": final_wood_bot1,
            "bot2_wood": final_wood_bot2,
            "reason": reason,
            "bot1_name": bot1_name,
            "bot2_name": bot2_name
        }
    }

    success = False
    resp = await post_with_retries("/matches/result", json_payload=payload)
    if resp is None:
        logger.error("Failed to connect to platform for match %s after retries.", match_id)
    elif resp.status_code == 200:
        logger.info(f"Successfully reported result for match {match_id} to platform.")
        success = True
    else:
        logger.error(f"Platform rejected result ({resp.status_code}): {resp.text}")

    if not success:
        # Local fallback
        fallback_dir = Path("result_fallback")
        fallback_dir.mkdir(exist_ok=True)
        fallback_path = fallback_dir / f"match_{match_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(fallback_path, "w") as f:
                json.dump(payload, f, indent=4)
            logger.info(f"Saved result to fallback: {fallback_path}")
        except Exception as e:
            logger.critical(f"CRITICAL: Failed to save fallback result: {e}")

    return success
