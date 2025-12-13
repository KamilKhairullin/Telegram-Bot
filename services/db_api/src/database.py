import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings

DB_URL = str(settings.DB_URL)

if not DB_URL:
    raise ValueError("❌ DB_URL env variable is missing! Check .env file.")

engine = create_async_engine(DB_URL, echo=True)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session_factory() as session:
        yield session
