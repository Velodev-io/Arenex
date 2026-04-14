import asyncio
import httpx
import logging
import json
from sqlalchemy.future import select
from datetime import datetime, timezone
from app.database import AsyncSessionLocal
from app.models import Match, Agent
from app.core.redis import get_redis
from app.services.handlers.chess import ChessHandler
from app.services.handlers.ttt import TTTHandler
from app.core.elo import calculate_elo

logger = logging.getLogger(__name__)

# --- Main Runner ---
async def _perform_agent_turn(client, handler, board, turn, match, match_id, agent_white, agent_black, db, history):
    current_agent = agent_white if turn == "white" else agent_black
    endpoint = f"{str(current_agent.endpoint_url).rstrip('/')}/move"
    payload = handler.get_payload(board, turn, match_id)

    try:
        resp = await client.post(endpoint, json=payload)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error(f"Agent forfeit: {e}")
        history.append({"agent": turn, "forfeit": True, "reason": str(e)})
        return "finished", ("black_wins" if turn == "white" else "white_wins")

    try:
        move_record = handler.process_move(board, turn, data)
        history.append(move_record)
        status, match_result = handler.check_result(board, turn)
    except Exception as e:
        history.append({"agent": turn, "forfeit": True, "reason": f"Bad move: {e}"})
        return "finished", ("black_wins" if turn == "white" else "white_wins")

    turn_next = "black" if turn == "white" else "white"
    match.history = list(history)
    await db.commit()

    try:
        redis = await get_redis()
        await redis.publish(f"match:{match_id}", json.dumps({"type": "move", "data": history[-1]}))
    except Exception as e:
        logger.error(f"Failed to publish move to Redis: {e}")
    
    return status, match_result, turn_next

def _update_match_stats(match, agent_white, agent_black, match_result):
    match.status, match.result = "finished", match_result
    if match_result:
        new_w, new_b = calculate_elo(agent_white.elo, agent_black.elo, match_result)
        agent_white.elo, agent_black.elo = new_w, new_b
        match.history.append({"event": "elo_updated", "white": new_w, "black": new_b})

async def _initialize_match_data(db, match_id):
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalars().first()
    if not match or match.is_practice:
        return None, None, None

    res_w = await db.execute(select(Agent).where(Agent.id == match.agent_white_id))
    agent_white = res_w.scalars().first()
    res_b = await db.execute(select(Agent).where(Agent.id == match.agent_black_id))
    agent_black = res_b.scalars().first()
    
    return match, agent_white, agent_black

async def process_match(match_id: int):
    async with AsyncSessionLocal() as db:
        match, agent_white, agent_black = await _initialize_match_data(db, match_id)
        if not match:
            return

        if not agent_white or not agent_black:
            match.status, match.result = "finished", "invalid_agents"
            await db.commit()
            return

        handler = ChessHandler if agent_white.game_type == "chess" else TTTHandler
        board, history, status, match_result, turn = handler.initialize_board(), [], "live", None, "white"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                while status == "live":
                    res = await _perform_agent_turn(client, handler, board, turn, match, match_id, agent_white, agent_black, db, history)
                    status, match_result, turn = res if len(res) == 3 else (res[0], res[1], turn)
                    await asyncio.sleep(0.2)
        except Exception as e:
            logger.error(f"Match loop crashed: {e}")
            status, match_result = "finished", "draw"

        _update_match_stats(match, agent_white, agent_black, match_result)
        await db.commit()

        try:
            redis = await get_redis()
            await redis.publish(f"match:{match_id}", json.dumps({"type": "finished", "result": match_result, "final_history": history}))
        except Exception as e:
            logger.error(f"Failed to publish match finish to Redis: {e}")

async def run_match(match_id: int):
    task = asyncio.create_task(process_match(match_id))
    task.add_done_callback(
        lambda t: logger.error(f"Match task failed: {t.exception()}") if t.exception() else None
    )
