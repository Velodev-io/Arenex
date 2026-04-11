from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

from fastapi_users.db import SQLAlchemyBaseUserTable

class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)

    agents = relationship("Agent", back_populates="owner")

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    endpoint_url = Column(String, nullable=False)
    game_type = Column(String, nullable=False) # 'chess' or 'tictactoe'
    elo = Column(Integer, default=1200)

    owner = relationship("User", back_populates="agents")

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    agent_white_id = Column(Integer, ForeignKey("agents.id"))
    agent_black_id = Column(Integer, ForeignKey("agents.id"))
    status = Column(String, default="live") # 'live', 'finished'
    result = Column(String, nullable=True)
    history = Column(JSON, default=list) # List of move objects
    
    # Relationships
    agent_white = relationship("Agent", foreign_keys=[agent_white_id])
    agent_black = relationship("Agent", foreign_keys=[agent_black_id])
