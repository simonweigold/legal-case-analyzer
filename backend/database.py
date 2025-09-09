from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from models.database import Base, User
import os

# Database URL - using SQLite with aiosqlite for async support
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./legal_analyzer.db")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async session maker
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    """Create database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncSession:
    """Dependency to get async database session."""
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Get user database instance."""
    yield SQLAlchemyUserDatabase(session, User)
