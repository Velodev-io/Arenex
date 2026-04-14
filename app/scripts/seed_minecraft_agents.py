import asyncio
from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.models import Agent

async def seed():
    async with AsyncSessionLocal() as db:
        # Check if they exist
        res = await db.execute(select(Agent).where(Agent.game_type == "minecraft_wood_race"))
        existing = res.scalars().all()
        if existing:
            print("Minecraft agents already exist.")
            return

        # Create two bots
        bot1 = Agent(
            name="ArenexBot1",
            owner_id=1, # Assume user 1 exists
            endpoint_url="http://192.168.1.25:8081",
            game_type="minecraft_wood_race",
            elo=1200
        )
        bot2 = Agent(
            name="ArenexBot2",
            owner_id=1,
            endpoint_url="http://192.168.1.25:8082",
            game_type="minecraft_wood_race",
            elo=1200
        )
        db.add(bot1)
        db.add(bot2)
        await db.commit()
        print("Created ArenexBot1 and ArenexBot2 (minecraft_wood_race)")

if __name__ == "__main__":
    asyncio.run(seed())
