import os
from redis import asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

async def get_redis():
    """Returns a redis client instance."""
    return aioredis.from_url(REDIS_URL, decode_responses=True)
