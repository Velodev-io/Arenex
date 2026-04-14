from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class MatchCreate(BaseModel):
    agent_white_id: Optional[int] = None
    agent_black_id: Optional[int] = None
    is_practice: bool = False
    difficulty: int = 10
    game_type: str = "chess"

class MatchRead(BaseModel):
    id: int
    agent_white_id: Optional[int] = None
    agent_black_id: Optional[int] = None
    status: str
    result: Optional[str] = None
    history: List[Any]
    timeline: Optional[List[Any]] = None
    had_live_viewer: bool = False
    is_practice: bool
    difficulty: Optional[int] = None
    game_type: str = "chess"

    class Config:
        from_attributes = True

class MatchResultSchema(BaseModel):
    match_id: str
    game_type: str
    winner_agent_id: int
    loser_agent_id: int
    result: str # "win", "draw"
    duration_seconds: int
    metadata: Dict[str, Any]
    timeline: Optional[List[Any]] = None
