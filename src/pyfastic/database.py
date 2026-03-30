from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from pyfastic.config import settings

# 1. De Engine: De verbinding met de database
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Zet op True voor SQL-logs tijdens het debuggen
)

# 2. De SessionMaker: Een herbruikbare fabriek voor sessies
# expire_on_commit=False is essentieel voor async om herlaad-fouten te voorkomen
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# 3. De Dependency: De generator die FastAPI gebruikt
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Levert een asynchrone databasesessie die automatisch wordt gesloten.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()