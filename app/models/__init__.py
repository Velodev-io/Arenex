from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
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
    agent_white_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    agent_black_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    status = Column(String, default="live") # 'live', 'finished'
    result = Column(String, nullable=True)
    history = Column(JSON, default=list) # List of move objects

    # Practice Mode fields
    is_practice = Column(Boolean, default=False)
    difficulty = Column(Integer, nullable=True)
    game_type = Column(String, default="chess")

    # Relationships
    agent_white = relationship("Agent", foreign_keys=[agent_white_id])
    agent_black = relationship("Agent", foreign_keys=[agent_black_id])
    comments = relationship("Comment", back_populates="match", cascade="all, delete-orphan")
    likes = relationship("MatchLike", back_populates="match", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    display_name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    match = relationship("Match", back_populates="comments")

class MatchLike(Base):
    __tablename__ = "match_likes"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))

    match = relationship("Match", back_populates="likes")
