import httpx
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Agent
from app.schemas.agent import AgentCreate, AgentRead

router = APIRouter()

@router.post("/", response_model=AgentRead, status_code=status.HTTP_201_CREATED)
async def register_agent(agent_in: AgentCreate, db: AsyncSession = Depends(get_db)):
    # Verify endpoint is responsive before saving
    ping_url = f"{str(agent_in.endpoint_url).rstrip('/')}/health"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(ping_url)
            response.raise_for_status()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to reach agent health endpoint at {ping_url}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent health endpoint returned error code {e.response.status_code}"
        )

    # Check uniqueness
    result = await db.execute(select(Agent).where(Agent.name == agent_in.name))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Agent name already registered")

    # Save agent
    new_agent = Agent(
        name=agent_in.name,
        endpoint_url=str(agent_in.endpoint_url),
        game_type=agent_in.game_type,
        elo=1200
    )
    db.add(new_agent)
    await db.commit()
    await db.refresh(new_agent)
    return new_agent

@router.get("/", response_model=List[AgentRead])
async def list_agents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent))
    agents = result.scalars().all()
    return agents

@router.get("/{agent_id}", response_model=AgentRead)
async def get_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalars().first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

from fastapi import Header
from app.database import settings, get_db

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    x_admin_api_key: str = Header(None)
):
    if x_admin_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Admin API Key"
        )

    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalars().first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    await db.delete(agent)
    await db.commit()
    return None
