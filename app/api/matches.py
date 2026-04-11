import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Match, Agent
from app.schemas.match import MatchCreate, MatchRead
from app.services.match_runner import run_match

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=MatchRead, status_code=status.HTTP_201_CREATED)
async def create_match(match_in: MatchCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    # Validate agents
    res_w = await db.execute(select(Agent).where(Agent.id == match_in.agent_white_id))
    agent_w = res_w.scalars().first()
    
    res_b = await db.execute(select(Agent).where(Agent.id == match_in.agent_black_id))
    agent_b = res_b.scalars().first()

    if not agent_w or not agent_b:
        raise HTTPException(status_code=400, detail="One or both agents not found")
        
    if agent_w.game_type != agent_b.game_type:
        raise HTTPException(status_code=400, detail="Agents must play the same game type")

    # Create match record
    new_match = Match(
        agent_white_id=agent_w.id,
        agent_black_id=agent_b.id,
        status="live",
        history=[]
    )
    db.add(new_match)
    await db.commit()
    await db.refresh(new_match)

    # Dispatch to background orchestration
    background_tasks.add_task(run_match, new_match.id)

    return new_match

@router.get("/{match_id}", response_model=MatchRead)
async def get_match(match_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match).where(Match.id == match_id))
    match_obj = result.scalars().first()
    
    if not match_obj:
        raise HTTPException(status_code=404, detail="Match not found")
        
    return match_obj

@router.get("/", response_model=List[MatchRead])
async def list_matches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Match))
    return result.scalars().all()
