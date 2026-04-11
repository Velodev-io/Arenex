from pydantic import BaseModel
from typing import List, Optional, Any

class MatchCreate(BaseModel):
    agent_white_id: int
    agent_black_id: int

class MatchRead(BaseModel):
    id: int
    agent_white_id: int
    agent_black_id: int
    status: str
    result: Optional[str] = None
    history: List[Any]

    class Config:
        from_attributes = True
