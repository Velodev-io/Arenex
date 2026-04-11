import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.future import select

from app.database import AsyncSessionLocal
from app.models import Match
from app.core.redis import get_redis

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/{match_id}")
async def match_websocket(websocket: WebSocket, match_id: int):
    await websocket.accept()
    
    # 1. Fetch current state for catchup
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Match).where(Match.id == match_id))
        match_obj = result.scalars().first()
        
        if not match_obj:
            await websocket.send_json({"type": "error", "detail": "Match not found"})
            await websocket.close()
            return
            
        # Send catchup event
        await websocket.send_json({
            "type": "catchup",
            "status": match_obj.status,
            "history": match_obj.history
        })
        
        # 2. If already completed, close cleanly
        if match_obj.status == "finished":
            await websocket.close()
            return

    # 3. Subscribe to Redis for new moves
    redis = await get_redis()
    pubsub = redis.pubsub()
    channel = f"match:{match_id}"
    await pubsub.subscribe(channel)
    
    try:
        while True:
            # Check if socket is still open (optional, but good practice)
            # We use a listener loop
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=5.0)
            if message:
                data = json.loads(message["data"])
                await websocket.send_json(data)
                
                # If we receive a 'finished' event, close after sending it
                if data.get("type") == "finished":
                    break
    except WebSocketDisconnect:
        logger.info(f"Spectator disconnected from match {match_id}")
    except Exception as e:
        logger.error(f"WebSocket error in match {match_id}: {e}")
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        # Ensure socket is closed if we broke the loop (e.g. on 'finished' event)
        try:
            await websocket.close()
        except:
            pass
