from pydantic import BaseModel
from typing import List, Optional, Any

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
    is_practice: bool
    difficulty: Optional[int] = None
    game_type: str = "chess"

    class Config:
        from_attributes = True
