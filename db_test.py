import sys
from os.path import abspath, dirname, join
from sqlalchemy import text

src_path = abspath(join(dirname(__file__), '.', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# print("DEBUG: Current sys.path:", sys.path)

from pyfastic.database import engine, async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

async def get_db_connection():
    try:
        async with async_session_maker() as session:
            test = text("SELECT 1")
            print("Database connection successful:")
            return await session.execute(test)
    except Exception as e:
        print("Database connection failed:", e)



if __name__ == "__main__":
    asyncio.run(get_db_connection())
