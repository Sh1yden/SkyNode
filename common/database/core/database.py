from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import declarative_base

from .get_engine import get_engine
from bot.src.core import get_logger

_lg = get_logger()

Base = declarative_base()
_lg.debug(f"Base из database.py: {id(Base)}")


async def init_database() -> (
    tuple[AsyncEngine | None, async_sessionmaker[AsyncSession]] | None
):
    """
    Initialize async database engine and session factory

    Returns:
        tuple: (engine, session_factory) | None
    """
    try:
        engine = await get_engine()
        SessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,  # Важно для async
        )

        _lg.debug(type(engine))
        _lg.info("Async database initialized successfully")

        return engine, SessionLocal

    except Exception as e:
        _lg.critical(f"Internall error: {e}")
