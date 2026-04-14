import logging
import json
from datetime import datetime
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Header
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db, settings
from app.models import Match, Agent
from app.schemas.match import MatchCreate, MatchRead, MatchResultSchema
from app.services.match_runner import run_match
from app.services.minecraft_match_runner import run_minecraft_match
from app.core.elo import calculate_elo
from app.core.redis import get_redis
import httpx

router = APIRouter()
logger = logging.getLogger(__name__)

class UserMove(BaseModel):
    move: str
    fen: Optional[str] = None
    board: Optional[List[List[Any]]] = None


class LiveViewerUpdate(BaseModel):
    had_live_viewer: bool = True

@router.get("/", response_model=List[MatchRead])
async def list_matches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match).order_by(Match.id.desc()))
    return result.scalars().all()

@router.post("/", response_model=MatchRead, status_code=status.HTTP_201_CREATED)
async def create_match(match_in: MatchCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    if match_in.is_practice:
        new_match = Match(
            is_practice=True,
            difficulty=match_in.difficulty,
            game_type=match_in.game_type,
            status="live",
            history=[]
        )
        db.add(new_match)
        await db.commit()
        await db.refresh(new_match)
        return new_match

    # Standard Match logic
    res_w = await db.execute(select(Agent).where(Agent.id == match_in.agent_white_id))
    agent_w = res_w.scalars().first()

    res_b = await db.execute(select(Agent).where(Agent.id == match_in.agent_black_id))
    agent_b = res_b.scalars().first()

    if not agent_w or not agent_b:
        raise HTTPException(status_code=400, detail="One or both agents not found")

    if agent_w.game_type != agent_b.game_type:
        raise HTTPException(status_code=400, detail="Agents must play the same game type")

    new_match = Match(
        agent_white_id=agent_w.id,
        agent_black_id=agent_b.id,
        game_type=agent_w.game_type,
        status="live",
        is_practice=False,
        history=[]
    )
    db.add(new_match)
    await db.commit()
    await db.refresh(new_match)

    if agent_w.game_type == "minecraft_wood_race":
        background_tasks.add_task(run_minecraft_match, new_match.id)
    else:
        background_tasks.add_task(run_match, new_match.id)
    return new_match

@router.post("/{match_id}/user-move")
async def register_user_move(match_id: int, user_move: UserMove, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match).where(Match.id == match_id))
    match_obj = result.scalars().first()
    if not match_obj or not match_obj.is_practice:
        raise HTTPException(status_code=400, detail="Practice match not found")

    # 1. Register User Move
    current_history = list(match_obj.history)
    user_entry = {
        "agent": "user",
        "move": user_move.move,
        "fen": user_move.fen,
        "board": user_move.board,
        "timestamp": str(datetime.utcnow())
    }
    current_history.append(user_entry)
    match_obj.history = current_history
    await db.commit()

    # Broadcast User Move
    redis = await get_redis()
    await redis.publish(f"match:{match_id}", json.dumps({"type": "move", "data": user_entry}))

    # 2. Trigger House Bot (Stockfish for chess, standard rule-based for TTT)
    bot_url = "http://localhost:8011/move" if match_obj.game_type == "chess" else "http://localhost:8010/move"

    bot_payload = {}
    if match_obj.game_type == "chess":
        bot_payload = {
            "board": user_move.fen,
            "your_color": "black",
            "game_id": str(match_id),
            "difficulty": match_obj.difficulty
        }
    else:
        bot_payload = {
            "board": user_move.board,
            "your_mark": "O",
            "game_id": str(match_id)
        }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(bot_url, json=bot_payload)
            resp.raise_for_status()
            data = resp.json()

            # Register Bot Move
            bot_entry = {
                "agent": "bot",
                "move": data.get("move") if match_obj.game_type == "chess" else {"row": data.get("row"), "col": data.get("col")},
                "fen": data.get("fen") if match_obj.game_type == "chess" else None,
                "board": data.get("board") if match_obj.game_type == "tictactoe" else None,
                "reasoning": data.get("reasoning", "Thinking..."),
                "timestamp": str(datetime.utcnow())
            }

            # Re-fetch for safety
            result = await db.execute(select(Match).where(Match.id == match_id))
            match_obj = result.scalars().first()
            current_history = list(match_obj.history)
            current_history.append(bot_entry)
            match_obj.history = current_history
            await db.commit()

            # Broadcast Bot Move
            await redis.publish(f"match:{match_id}", json.dumps({"type": "move", "data": bot_entry}))

    except Exception as e:
        logger.error(f"House bot error: {e}")
        pass

    return {"status": "ok"}

@router.post("/result")
async def receive_match_result(result_in: MatchResultSchema, db: AsyncSession = Depends(get_db)):
    # 1. Find match in DB
    try:
        match_id_int = int(result_in.match_id)
    except ValueError:
        # If match_id is not an int, it might be a test match or we need to handle it
        raise HTTPException(status_code=400, detail="Invalid match_id format")

    result = await db.execute(select(Match).where(Match.id == match_id_int))
    match_obj = result.scalars().first()
    if not match_obj:
        raise HTTPException(status_code=404, detail="Match not found")

    if match_obj.status == "finished":
        return {"status": "already_processed"}

    # 2. Update match status
    match_obj.status = "finished"
    match_obj.result = result_in.result # "win" or "draw"
    match_obj.timeline = result_in.timeline
    
    # 3. Update ELO
    res_w = await db.execute(select(Agent).where(Agent.id == match_obj.agent_white_id))
    agent_white = res_w.scalars().first()
    res_b = await db.execute(select(Agent).where(Agent.id == match_obj.agent_black_id))
    agent_black = res_b.scalars().first()

    if agent_white and agent_black:
        # Determine internal result string for elo calc
        # MatchResultSchema has result="win" or "draw"
        # and winner_agent_id / loser_agent_id
        elo_result = "draw"
        if result_in.result == "win":
            if result_in.winner_agent_id == agent_white.id:
                elo_result = "white_wins"
            else:
                elo_result = "black_wins"
        
        new_w, new_b = calculate_elo(agent_white.elo, agent_black.elo, elo_result)
        agent_white.elo, agent_black.elo = new_w, new_b
        
        # Log to history
        match_obj.history.append({
            "event": "match_finished",
            "winner_agent_id": result_in.winner_agent_id,
            "reason": result_in.metadata.get("reason", "unknown"),
            "duration": result_in.duration_seconds,
            "elo_updated": {"white": new_w, "black": new_b}
        })
    
    await db.commit()

    # 4. Broadcast result
    try:
        redis = await get_redis()
        await redis.publish(f"match:{match_obj.id}", json.dumps({
            "type": "finished",
            "result": match_obj.result,
            "metadata": result_in.metadata
        }))
    except Exception as e:
        logger.error(f"Failed to publish match finish to Redis: {e}")

    return {"status": "ok"}


@router.post("/{match_id}/live-viewer", status_code=status.HTTP_204_NO_CONTENT)
async def mark_match_live_viewer(
    match_id: int,
    update: LiveViewerUpdate,
    db: AsyncSession = Depends(get_db),
    x_admin_api_key: Optional[str] = Header(None),
):
    if x_admin_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Admin API Key",
        )

    result = await db.execute(select(Match).where(Match.id == match_id))
    match_obj = result.scalars().first()
    if not match_obj:
        raise HTTPException(status_code=404, detail="Match not found")

    match_obj.had_live_viewer = update.had_live_viewer
    await db.commit()
    return None

@router.get("/{match_id}", response_model=MatchRead)
async def get_match(match_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match).where(Match.id == match_id))
    match_obj = result.scalars().first()

    if not match_obj:
        raise HTTPException(status_code=404, detail="Match not found")

    return match_obj

@router.get("/{match_id}/minecraft/replay")
async def get_minecraft_replay(match_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match).where(Match.id == match_id))
    match_obj = result.scalars().first()
    if not match_obj:
        raise HTTPException(status_code=404, detail="Match not found")
    return {"timeline": match_obj.timeline}
