from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import DeclarativeBase


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"

engine: AsyncEngine = create_async_engine(
    url = SQLALCHEMY_DATABASE_URL,
    connect_args = {
        "check_same_thread": False,
    },
)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind = engine,
    class_ = AsyncSession,
    expire_on_commit = False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
