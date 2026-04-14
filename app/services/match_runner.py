import asyncio
import logging
import httpx
import json
from datetime import datetime, timezone
from sqlalchemy.future import select

from app.database import AsyncSessionLocal
from app.models import Match, Agent
from app.core.redis import get_redis
from app.services.minecraft_match_runner import run_minecraft_match
from app.services.handlers.chess import ChessHandler
from app.services.handlers.ttt import TTTHandler

logger = logging.getLogger(__name__)

async def run_match(match_id: int):
    """Background task to run a match and broadcast moves."""
    logger.info(f"Starting match runner for match_id: {match_id}")
    
    async with AsyncSessionLocal() as db:
        # Fetch match and agents
        result = await db.execute(select(Match).where(Match.id == match_id))
        match = result.scalars().first()
        if not match:
            logger.error(f"Match {match_id} not found")
            return

        res_w = await db.execute(select(Agent).where(Agent.id == match.agent_white_id))
        agent_w = res_w.scalars().first()
        res_b = await db.execute(select(Agent).where(Agent.id == match.agent_black_id))
        agent_b = res_b.scalars().first()
        
        if not agent_w or not agent_b:
            logger.error(f"Match {match_id} is missing agents")
            return

        # 1. Dispatch Minecraft matches to specialized runner
        if agent_w.game_type == "minecraft_wood_race":
            await run_minecraft_match(match_id)
            return

        # 2. Handle turn-based games (Chess, Tic-Tac-Toe)
        handler = ChessHandler if agent_w.game_type == "chess" else TTTHandler
        board = handler.initialize_board()
        
        # Reset history for fresh start
        match.history = []
        await db.commit()

        redis = await get_redis()
        
        turn = "white"
        game_status = "live"
        
        max_turns = 100 # Safety limit
        turn_count = 0
        
        while game_status == "live" and turn_count < max_turns:
            turn_count += 1
            current_agent = agent_w if turn == "white" else agent_b
            payload = handler.get_payload(board, turn, match_id)
            
            try:
                logger.info(f"Match {match_id}: Requesting move from {current_agent.name} ({turn})")
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(current_agent.endpoint_url, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                
                # Process the move
                entry = handler.process_move(board, turn, data)
                
                # Persist move
                # Re-fetch match to ensure we have current session state
                result = await db.execute(select(Match).where(Match.id == match_id))
                match = result.scalars().first()
                history = list(match.history)
                history.append(entry)
                match.history = history
                await db.commit()
                
                # Broadcast to spectators
                await redis.publish(f"match:{match_id}", json.dumps({"type": "move", "data": entry}))
                
                # Check for game over
                game_status, result_str = handler.check_result(board, turn)
                if game_status == "finished":
                    match.status = "finished"
                    match.result = result_str
                    await db.commit()
                    await redis.publish(f"match:{match_id}", json.dumps({
                        "type": "status", 
                        "data": "finished", 
                        "result": result_str
                    }))
                    logger.info(f"Match {match_id} finished: {result_str}")
                    break
                
                # Switch turns
                turn = "black" if turn == "white" else "white"
                await asyncio.sleep(1) # Pace the broadcasting
                
            except Exception as e:
                logger.error(f"Match {match_id} runtime error: {e}")
                match.status = "finished"
                match.result = "error"
                await db.commit()
                break

        if turn_count >= max_turns:
            logger.warning(f"Match {match_id} hit move limit ({max_turns})")
            match.status = "finished"
            match.result = "draw_limit"
            await db.commit()
