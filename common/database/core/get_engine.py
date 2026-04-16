from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from bot.src.utils import settings


async def get_engine(prj_status=settings.PROJECT_STATUS) -> AsyncEngine | None:
    """
    Create async database engine

    Args:
        db_status: Database status ('development' or 'product')

    Returns:
        AsyncEngine: Async SQLAlchemy engine
    """
    from bot.src.core import get_logger

    _lg = get_logger()
    try:
        if prj_status == "development":
            _lg.debug(f"Using SQLite: {settings.SQLITE_DB_URL}")
            return create_async_engine(settings.SQLITE_DB_URL)

        elif prj_status == "product":
            _lg.debug(f"=== PostgreSQL Connection Details ===")
            _lg.debug(f"ASYNCPG: {settings.POSTGRES_ASYNCPG}")
            _lg.debug(f"Host: {settings.POSTGRES_HOST}")
            _lg.debug(f"Port: {settings.POSTGRES_PORT}")
            _lg.debug(f"Database: {settings.POSTGRES_DB}")
            _lg.debug(f"User: {settings.POSTGRES_USER}")

            return create_async_engine(
                f"postgresql+"
                f"{settings.POSTGRES_ASYNCPG}"
                f"://{settings.POSTGRES_USER}:"
                f"{settings.POSTGRES_PASSWORD}@"
                f"{settings.POSTGRES_HOST}:"
                f"{settings.POSTGRES_PORT}/"
                f"{settings.POSTGRES_DB}"
            )

        else:
            _lg.error(f"Unknown database status: {prj_status}")
            raise ValueError(f"Unknown database status: {prj_status}")
    except Exception as e:
        _lg.error(f"Internal error: {e}.")


if __name__ == "__main__":
    print(
        f"postgresql+"
        f"{settings.POSTGRES_ASYNCPG}"
        f"://{settings.POSTGRES_USER}:"
        f"{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_HOST}:"
        f"{settings.POSTGRES_PORT}/"
        f"{settings.POSTGRES_DB}"
    )
