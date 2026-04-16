from contextlib import asynccontextmanager

from fastapi import FastAPI

from bot.src.utils import api_cleanup
from common.database.repositories.factory import create_repositories
from common.database.core import init_database
from bot.src.core import get_logger, setup_logging
from admin.main import setup_admin

setup_logging(level="DEBUG")
_lg = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Включение
    _lg.debug("API initialization...")
    try:
        # Инициализация БД
        engine, SessionLocal = await init_database()  # type: ignore

        await setup_admin(app=app, engine=engine)

        # Создание репозиториев
        repos = await create_repositories(SessionLocal, engine)  # type: ignore
        _lg.debug("Repositories created")

        app.state.repos = repos

        _lg.info("API initialized.")
    except Exception as e:
        _lg.critical(f"Failed to initialize API: {e}", exc_info=True)
        raise

    yield  # Работа

    # Выключение
    try:
        _lg.debug("API closing...")
        await api_cleanup(app.state.repos)
    except Exception as e:
        _lg.critical(f"Failed to close API: {e}", exc_info=True)
        raise
