from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine

from common.database.repositories.user_repository import UserRepository
from common.database.repositories.weather_repository import WeatherRepository

from bot.src.utils.db_utils import get_database_methods
from common.database.core.database import Base


async def create_repositories(
    session_factory: async_sessionmaker,
    engine: AsyncEngine,
) -> dict:
    """Factory function to create all repository instances."""
    # Инициализация БД

    db_methods = await get_database_methods(session_factory, Base, engine)

    return {
        "user_repo": UserRepository(db_methods),
        "weather_repo": WeatherRepository(db_methods),
    }
