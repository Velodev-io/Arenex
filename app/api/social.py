from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database import AsyncSessionLocal
from app.models import Match, Comment, MatchLike
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()

class CommentCreate(BaseModel):
    display_name: str
    content: str

class CommentRead(BaseModel):
    id: int
    display_name: str
    content: str
    created_at: datetime

class SocialStats(BaseModel):
    likes: int
    comments: List[CommentRead]

@router.post("/{match_id}/like")
async def like_match(match_id: int):
    async with AsyncSessionLocal() as db:
        match_res = await db.execute(select(Match).where(Match.id == match_id))
        if not match_res.scalars().first():
            raise HTTPException(status_code=404, detail="Match not found")
            
        like = MatchLike(match_id=match_id)
        db.add(like)
        await db.commit()
        
        # Return new count
        result = await db.execute(select(MatchLike).where(MatchLike.match_id == match_id))
        count = len(result.scalars().all())
        return {"likes": count}

@router.post("/{match_id}/comment", response_model=CommentRead)
async def post_comment(match_id: int, comment_data: CommentCreate):
    async with AsyncSessionLocal() as db:
        match_res = await db.execute(select(Match).where(Match.id == match_id))
        if not match_res.scalars().first():
            raise HTTPException(status_code=404, detail="Match not found")
            
        comment = Comment(
            match_id=match_id,
            display_name=comment_data.display_name,
            content=comment_data.content
        )
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment

@router.get("/{match_id}/stats", response_model=SocialStats)
async def get_stats(match_id: int):
    async with AsyncSessionLocal() as db:
        # Get likes
        res_likes = await db.execute(select(MatchLike).where(MatchLike.match_id == match_id))
        likes_count = len(res_likes.scalars().all())
        
        # Get comments
        res_comments = await db.execute(
            select(Comment)
            .where(Comment.match_id == match_id)
            .order_by(Comment.created_at.desc())
        )
        comments = res_comments.scalars().all()
        
        return {
            "likes": likes_count,
            "comments": comments
        }
