import logging
import json
from datetime import datetime
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Match, Agent
from app.schemas.match import MatchCreate, MatchRead
from app.services.match_runner import run_match
from app.core.redis import get_redis
import httpx

router = APIRouter()
logger = logging.getLogger(__name__)

class UserMove(BaseModel):
    move: str
    fen: Optional[str] = None
    board: Optional[List[List[Any]]] = None

@router.post("", response_model=MatchRead, status_code=status.HTTP_201_CREATED)
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
        status="live",
        is_practice=False,
        history=[]
    )
    db.add(new_match)
    await db.commit()
    await db.refresh(new_match)

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
    bot_url = "http://192.168.1.25:8011/move" if match_obj.game_type == "chess" else "http://192.168.1.25:8010/move"

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

@router.get("/{match_id}", response_model=MatchRead)
async def get_match(match_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match).where(Match.id == match_id))
    match_obj = result.scalars().first()

    if not match_obj:
        raise HTTPException(status_code=404, detail="Match not found")

    return match_obj

@router.get("", response_model=List[MatchRead])
async def list_matches(db: AsyncSession = Depends(get_db)):
    # Standard matches only (exclude practice from main feed)
    result = await db.execute(select(Match).where(Match.is_practice == False))
    return result.scalars().all()
