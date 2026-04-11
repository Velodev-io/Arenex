import asyncio
from app.database import engine
from sqlalchemy import inspect

async def check_db():
    print("Checking database tables...")
    async with engine.connect() as conn:
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        print(f"Detected Tables: {tables}")
        # Verify specific tables exist
        required_tables = {"users", "agents", "matches"}
        present = required_tables.intersection(set(tables))
        if present == required_tables:
            print("SUCCESS: All core tables are present.")
        else:
            missing = required_tables - present
            print(f"FAILURE: Missing tables: {missing}")

if __name__ == "__main__":
    asyncio.run(check_db())
