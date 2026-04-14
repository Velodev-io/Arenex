from pydantic import BaseModel, HttpUrl
from typing import Optional

class AgentBase(BaseModel):
    name: str
    endpoint_url: HttpUrl
    game_type: str

class AgentCreate(AgentBase):
    pass

class AgentRead(AgentBase):
    id: int
    elo: int
    owner_id: Optional[int] = None

    class Config:
        from_attributes = True
