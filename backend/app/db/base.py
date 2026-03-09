"""Database base configuration and session management."""
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()


def _normalize_database_url(database_url: str) -> str:
    prefix = "sqlite+aiosqlite:///"
    if not database_url.startswith(prefix):
        return database_url

    sqlite_path = database_url[len(prefix):]
    if sqlite_path in {":memory:", ""}:
        return database_url

    path_obj = Path(sqlite_path)
    if path_obj.is_absolute():
        return database_url

    absolute_path = (settings.BASE_DIR / path_obj).resolve()
    return f"{prefix}{absolute_path.as_posix()}"


DATABASE_URL = _normalize_database_url(settings.DATABASE_URL)

# Create async engine
async_engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Create async session maker
async_session_maker = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Alias for migration scripts
AsyncSessionLocal = async_session_maker


# Define base class for models
class Base(DeclarativeBase):
    """Base class for all database models."""
    metadata = MetaData()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.

    Yields:
        AsyncSession: Database session
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database by creating all tables.
    """
    # Import all models so Base.metadata knows about them
    import app.db.models  # noqa: F401

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
