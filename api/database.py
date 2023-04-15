from typing import AsyncGenerator
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER, COUNT_MAX_CONNECTIONS_DB,\
    LIVE_POOL_DB_CONNECTIONS, COUNT_OVERFLOW_POOL

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

metadata = MetaData()
engine = create_async_engine(DATABASE_URL, pool_size=COUNT_MAX_CONNECTIONS_DB, max_overflow=COUNT_OVERFLOW_POOL,
                             poolclass=QueuePool, pool_recycle=LIVE_POOL_DB_CONNECTIONS)
async_session_maker = sessionmaker(engine, class_=AsyncSession)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
