from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from models.database import Base, User
import os

# Database URL - using SQLite with aiosqlite for async support
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./legal_analyzer.db")

# Create async engine with connection pooling optimized for streaming scenarios
engine = create_async_engine(
    DATABASE_URL, 
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,  # Increased pool size for concurrent operations
    max_overflow=20,  # Allow more overflow connections
    pool_timeout=30,  # Timeout for getting connection from pool
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create async session maker with optimized settings
async_session_maker = async_sessionmaker(
    engine, 
    expire_on_commit=False,
    autoflush=True,  # Automatically flush pending changes
    autocommit=False  # Explicit transaction control
)


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


async def get_streaming_session():
    """
    Create a new database session specifically for streaming operations.
    This ensures proper connection lifecycle management in long-running operations.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            # Ensure session is properly closed
            await session.close()
