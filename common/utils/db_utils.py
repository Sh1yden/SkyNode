import sys
from pathlib import Path

# Для прямого запуска файла
if __name__ == "__main__":
    # Добавляем bot/ в sys.path
    bot_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(bot_dir))

from typing import Type, Any, TypeVar

from aiogram.types import User

from sqlalchemy import inspect, exists, select, func, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from common.core import get_logger
from common.utils import RedisCache

# TypeVar для generic типизации
T = TypeVar("T", bound=DeclarativeBase)


class MethodsOfDatabase:
    """Universal methods for SQLite and PostgreSQL."""

    def __init__(
            self,
            session_factory: async_sessionmaker[AsyncSession],
            base: Type[DeclarativeBase],
            engine: AsyncEngine | None,
    ):
        """
        Initialize database methods

        Args:
            session_factory: SQLAlchemy session factory
            base: Declarative base class
            engine: Database engine
        """
        self._lg = get_logger()
        self._lg.debug("Initializing MethodsOfDatabase.")

        if engine is None:
            self._lg.critical("Engine is None!")
            raise ValueError("Database engine is required!")

        self.session_factory = session_factory
        self.base = base
        self.engine = engine
        self.cache = RedisCache()  # Создаём, но не подключаемся

    def _get_session(self) -> AsyncSession:
        """
        Create new database session

        Returns:
            Session: New SQLAlchemy session
        """
        return self.session_factory()

    async def create_tables_and_database(self) -> bool:
        """Create all database tables if they don't exist"""
        async with self.engine.begin() as conn:
            try:
                from common.database.models import (
                    UserAllInfo,
                    WeatherAllInfo,
                    Admin,
                )  # noqa: F401 # нужно для правильного создания таблиц

                def get_existing_tables(sync_conn):
                    return inspect(sync_conn).get_table_names()

                def create_all_tables(sync_conn):
                    return self.base.metadata.create_all(sync_conn)

                existing_tables = await conn.run_sync(get_existing_tables)

                if existing_tables:
                    self._lg.debug(f"Found existing tables: {existing_tables}.")
                else:
                    self._lg.debug("No existing tables found, creating...")

                # Создаём таблицы
                await conn.run_sync(create_all_tables)

                # Проверяем
                new_tables = await conn.run_sync(get_existing_tables)
                self._lg.debug(f"Database tables ready: {new_tables}.")

                return True

            except Exception as e:
                self._lg.critical(f"Failed to create tables: {e}.", exc_info=True)
                return False

    async def initialize_cache(self) -> None:
        """Initialize Redis cache connection."""
        try:
            await self.cache.connect()  # type: ignore
            self._lg.info("Redis cache initialized")
        except Exception as e:
            self._lg.error(
                f"Failed to initialize Redis cache: {e}. Continue with no cache."
            )
            # Можно продолжить без кэша
            self.cache = None

    # ==== Admin Methods ====
    async def add_admin(self, model: Type[T], user_id: int) -> bool:
        """Create new admin."""
        async with self._get_session() as session:
            try:
                new_admin = model(user_id=user_id)
                session.add(new_admin)
                await session.commit()
                return True

            except Exception as e:
                await session.rollback()
                self._lg.error(f"Failed to add admin {user_id}: {e}")
                return False

    async def is_admin(self, model: Type[T], user_id: int) -> bool:
        """Check if user is admin."""
        async with self._get_session() as session:
            try:
                # Используем EXISTS для максимальной скорости
                stmt = select(exists().where(model.user_id == user_id))  # type: ignore
                result = await session.scalar(stmt)
                return bool(result)

            except Exception as e:
                self._lg.error(f"Error checking admin status: {e}")
                return False

    async def check_status_db(self) -> bool:
        """Check status of database."""
        async with self._get_session() as session:
            try:
                result = await session.scalar(text("SELECT 1"))
                return bool(result)

            except Exception as e:
                self._lg.error(f"Error checking status of database: {e}")
                return False

    async def check_status_redis(self) -> bool:
        """Check status of Redis."""
        try:
            result = await self.cache.ping()
            return bool(result)

        except Exception as e:
            self._lg.error(f"Error checking status of Redis: {e}")
            return False

    # ==== User Methods ====
    async def create_one_user(
            self,
            model: Type[T],
            user: User | None = None,
            **kwargs: Any,
    ) -> tuple[bool, str]:
        """
        Create one user in database

        Args:
            model: Model class (e.g., UserAllInfo)
            user: Aiogram User object
            **kwargs: Additional fields to set

        Returns:
            tuple[bool, str]: (success, message)

        Example:
            success, msg = await db.create_one_user(
                model=UserAllInfo,
                user=telegram_user,
                city="Moscow"
            )
        """
        async with self._get_session() as session:
            try:
                # Проверка на существование
                user_id = user.id if user else kwargs.get("user_id")

                # Оптимизированная проверка через EXISTS
                if user_id:
                    exists_stmt = select(exists().where(model.user_id == user_id))  # type: ignore
                    user_exists = await session.scalar(exists_stmt)

                    if user_exists:
                        self._lg.debug(f"User {user_id} already exists.")
                        return False, f"User {user_id} already exists."

                # Подготовка данных из User объекта
                data = {}
                if user is not None:
                    data = {
                        "user_id": user.id,
                        "is_bot": user.is_bot,
                        "is_premium": user.is_premium,
                        "language_code": user.language_code,
                        "supports_inline_queries": getattr(
                            user, "supports_inline_queries", False
                        ),
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    }

                # Добавляем/перезаписываем дополнительными параметрами
                data.update(kwargs)

                # Создание записи
                new_user = model(**data)
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)

                # Redis cache
                await self.cache.set(key=user_id, data=data)  # type: ignore

                self._lg.debug(f"User created: {new_user.user_id}.")  # type: ignore
                return True, f"User {new_user.user_id} created successfully."  # type: ignore

            except Exception as e:
                await session.rollback()
                self._lg.error(f"Failed to create user: {e}.", exc_info=True)
                return False, f"Error: {str(e)}."

    async def delete_one_user_by_id(
            self,
            model: Type[T],
            user_id: int,
    ) -> tuple[bool, str]:
        """
        Delete one user by ID

        Args:
            model: Model class
            user_id: Telegram user ID

        Returns:
            tuple[bool, str]: (success, message)
        """
        async with self._get_session() as session:
            try:
                # Находим пользователя
                stmt = select(model).where(model.user_id == user_id)  # type: ignore
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if user is None:
                    self._lg.warning(f"User {user_id} not found for deletion.")
                    return False, f"User {user_id} not found."

                # Сохраняем данные для лога
                username = getattr(user, "username", "unknown")

                # Удаляем
                await session.delete(user)
                await session.commit()

                # Redis cache
                await self.cache.delete(key=user_id)  # type: ignore

                self._lg.debug(f"User deleted: {user_id} ({username}).")
                return True, f"User {user_id} deleted successfully."

            except Exception as e:
                await session.rollback()
                self._lg.error(f"Failed to delete user {user_id}: {e}.", exc_info=True)
                return False, f"Error: {str(e)}"

    async def update_one_user_by_id(
            self,
            model: Type[T],
            user_id: int,
            **kwargs: Any,
    ) -> tuple[bool, str, dict[str, Any] | None]:
        """
        Update one user by ID

        Args:
            model: Model class
            user_id: Telegram user ID
            **kwargs: Fields to update

        Returns:
            tuple[bool, str, dict]: (success, message, updated_fields)

        Example:
            success, msg, changes = await db.update_one_user_by_id(
                model=UserAllInfo,
                user_id=123456,
                first_name="New Name",
                city="Moscow"
            )
        """
        async with self._get_session() as session:
            try:
                # Находим пользователя
                stmt = select(model).where(model.user_id == user_id)  # type: ignore
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if user is None:
                    self._lg.warning(f"User {user_id} not found for update.")
                    return False, f"User {user_id} not found.", None

                if not kwargs:
                    self._lg.warning("No fields provided for update.")
                    return False, "No fields to update.", None

                updated_fields = {}
                invalid_fields = []

                # Обновляем только изменённые поля
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        old_value = getattr(user, key)
                        if old_value != value:
                            setattr(user, key, value)
                            updated_fields[key] = {"old": old_value, "new": value}
                    else:
                        invalid_fields.append(key)

                if invalid_fields:
                    self._lg.warning(f"Invalid fields ignored: {invalid_fields}.")

                if not updated_fields:
                    return True, "No changes detected.", {}

                await session.commit()
                await session.refresh(user)

                # Redis cache
                await self.cache.update(user_id, updated_fields)  # type: ignore

                self._lg.debug(
                    f"User {user_id} updated: {list(updated_fields.keys())}."
                )
                return True, f"Updated {len(updated_fields)} fields.", updated_fields

            except Exception as e:
                await session.rollback()
                self._lg.error(f"Failed to update user {user_id}: {e}.", exc_info=True)
                return False, f"Error: {str(e)}", None

    async def user_exists(self, model: Type[T], user_id: int) -> bool:
        """
        Check if user exists in database

        Args:
            model: Model class
            user_id: Telegram user ID

        Returns:
            bool: True if user exists, False otherwise
        """
        # Проверяем кэш
        if await self.cache.exists(user_id):  # type: ignore
            return True

        async with self._get_session() as session:
            try:
                # Используем EXISTS для оптимизации
                stmt = select(exists().where(model.user_id == user_id))  # type: ignore
                result = await session.scalar(stmt)
                return bool(result)

            except Exception as e:
                self._lg.error(f"Error checking user existence: {e}.")
                return False

    async def user_location_exists(self, model: Type[T], user_id: int) -> bool:
        """
        Check if user location exists in database

        Args:
            model: Model class
            user_id: Telegram user ID

        Returns:
            bool: True if user location exists, False otherwise
        """
        try:
            # Проверяем кэш
            cached_data = await self.cache.get(user_id)  # type: ignore

            if cached_data:
                self._lg.debug(f"Cached data (deserialized) - {cached_data}")

                if cached_data and isinstance(cached_data, dict):
                    city = cached_data.get("city")
                    lat = cached_data.get("latitude")
                    lon = cached_data.get("longitude")

                    if city or lat or lon:
                        self._lg.debug(
                            f"User {user_id} location found in cache: city={city}, lat={lat}, lon={lon}"
                        )
                        return True

                    self._lg.debug(f"User {user_id} location not found in cache")
                    return False
                else:
                    self._lg.debug("Cached data not isinstance!!!")
                    return False

            else:
                # Проверяем БД
                self._lg.debug(f"No cache for user {user_id}, checking database")

                async with self._get_session() as session:
                    stmt = select(model).where(model.user_id == user_id)  # type: ignore
                    result = await session.execute(stmt)
                    user = result.scalar_one_or_none()

                    if not user:
                        self._lg.warning(f"User {user_id} not found in database")
                        return False

                    city = getattr(user, "city", None)
                    lat = getattr(user, "latitude", None)
                    lon = getattr(user, "longitude", None)

                    if city or lat or lon:
                        self._lg.debug(
                            f"User {user_id} location found in DB: city={city}, lat={lat}, lon={lon}"
                        )
                        return True

                    self._lg.debug(f"User {user_id} location not found in DB")
                    return False

        except Exception as e:
            self._lg.error(f"Error checking user location existence: {e}.")
            return False

    async def find_by_one_user_id(
            self,
            model: Type[T],
            user_id: int,
            as_dict: bool = True,
    ) -> T | dict[str, Any] | None:
        """
        Find one user by ID

        Args:
            model: Model class
            user_id: Telegram user ID
            as_dict: Return as dictionary instead of model instance

        Returns:
            Model instance, dictionary, or None if not found
        """
        try:
            # Проверяем кэш
            cached_data = await self.cache.get(user_id)  # type: ignore
            if cached_data:
                return cached_data

            async with self._get_session() as session:
                stmt = select(model).where(model.user_id == user_id)  # type: ignore
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if user is None:
                    self._lg.debug(f"User {user_id} not found.")
                    return None

                if as_dict:
                    # Преобразуем в словарь
                    result_dict = {
                        column.name: getattr(user, column.name)
                        for column in model.__table__.columns
                    }
                    self._lg.debug(f"User {user_id} found and returned as dict.")
                    return result_dict
                else:
                    # Для async нужно make_transient или detach
                    # make_transient удаляет объект из session
                    from sqlalchemy.orm import make_transient

                    make_transient(user)
                    self._lg.debug(f"User {user_id} found and returned as object.")
                    return user

        except Exception as e:
            self._lg.error(f"Error finding user {user_id}: {e}.")
            return None

    async def find_users(  # TODO
            self,
            model: Type[T],
            filters: dict[str, Any] | None = None,
            limit: int = 100,
            offset: int = 0,
            as_dict: bool = True,
    ) -> list[dict[str, Any]] | list[T]:
        """
        Find multiple users with filters

        Args:
            model: Model class
            filters: Dictionary of field:value pairs for filtering
            limit: Maximum number of results
            offset: Skip first N results
            as_dict: Return as list of dictionaries

        Returns:
            List of users (as dicts or model instances)

        Example:
            users = await db.find_users(
                model=UserAllInfo,
                filters={"is_premium": True, "language_code": "ru"},
                limit=50
            )
        """
        async with self._get_session() as session:
            try:
                stmt = select(model)

                # Применяем фильтры
                if filters:
                    for key, value in filters.items():
                        if hasattr(model, key):
                            stmt = stmt.where(getattr(model, key) == value)
                        else:
                            self._lg.warning(f"Invalid filter field: {key}.")

                # Применяем лимиты
                stmt = stmt.limit(limit).offset(offset)

                # Выполняем запрос
                result = await session.execute(stmt)
                users = result.scalars().all()

                self._lg.debug(f"Found {len(users)} users with filters: {filters}.")

                if as_dict:
                    return [
                        {
                            col.name: getattr(user, col.name)
                            for col in model.__table__.columns
                        }
                        for user in users
                    ]
                else:
                    # Делаем объекты transient
                    from sqlalchemy.orm import make_transient

                    for user in users:
                        make_transient(user)
                    return list(users)

            except Exception as e:
                self._lg.error(f"Error finding users: {e}.", exc_info=True)
                return []

    async def count_users(
            self,
            model: Type[T],
            filters: dict[str, Any] | None = None,
    ) -> int:
        """
        Count users with optional filters

        Args:
            model: Model class
            filters: Dictionary of field:value pairs for filtering

        Returns:
            int: Number of users matching filters

        Example:
            premium_count = await db.count_users(
                model=UserAllInfo,
                filters={"is_premium": True}
            )
        """
        async with self._get_session() as session:
            try:
                stmt = select(func.count()).select_from(model)

                if filters:
                    for key, value in filters.items():
                        if hasattr(model, key):
                            stmt = stmt.where(getattr(model, key) == value)
                        else:
                            self._lg.warning(
                                f"Invalid filter field: {key}. For model {model.__name__}."
                            )

                count = await session.scalar(stmt)

                self._lg.debug(f"Count: {count} users with filters: {filters}.")

                return count or 0

            except Exception as e:
                self._lg.error(f"Error counting users: {e}.")
                return 0

    async def create_many_users(  # TODO
            self,
            model: Type[T],
            users_data: list[dict[str, Any]],
    ) -> tuple[int, int, list[str]]:
        """
        Create multiple users at once (batch operation)

        Args:
            model: Model class
            users_data: List of dictionaries with user data

        Returns:
            tuple[int, int, list]: (created_count, failed_count, error_messages)

        Example:
            created, failed, errors = await db.create_many_users(
                model=UserAllInfo,
                users_data=[
                    {"user_id": 1, "first_name": "User1", "is_bot": False},
                    {"user_id": 2, "first_name": "User2", "is_bot": False},
                ]
            )
        """
        async with self._get_session() as session:
            created = 0
            failed = 0
            errors = []

            try:
                for user_data in users_data:
                    try:
                        new_user = model(**user_data)
                        session.add(new_user)
                        created += 1
                    except Exception as e:
                        error_msg = (
                            f"Failed to add user {user_data.get('user_id')}: {e}"
                        )
                        self._lg.warning(error_msg)
                        errors.append(error_msg)
                        failed += 1

                await session.commit()

                self._lg.debug(
                    f"Batch creation: {created} users created, {failed} failed."
                )

                return created, failed, errors

            except Exception as e:
                await session.rollback()
                self._lg.error(f"Batch creation failed: {e}.", exc_info=True)
                return 0, len(users_data), [f"Batch error: {str(e)}"]

    async def get_all_user_ids(
            self,
            model: Type[T],
            limit: int | None = 100,
            offset: int | None = 0,
    ) -> list[int]:
        """
        Get list of all user IDs

        Args:
            model: Model class
            limit:
            offset:

        Returns:
            list[int]: List of user IDs
        """
        async with self._get_session() as session:
            try:
                stmt = select(model.user_id).limit(limit).offset(offset)  # type: ignore
                result = await session.execute(stmt)
                user_ids = result.scalars().all()

                self._lg.debug(f"Retrieved {len(user_ids)} user IDs.")
                return list(user_ids)

            except Exception as e:
                self._lg.error(f"Error getting user IDs: {e}.")
                return []

    # ==== Weather Methods ====
    async def create_weather_cache(
            self,
            model: Type[T],
            weather_id: str,
            **kwargs: Any,
    ) -> tuple[bool, str]:
        """
        Create weather cache entry

        Args:
            model: Model class (WeatherAllInfo)
            weather_id: Unique weather cache identifier
            **kwargs: Additional fields to set

        Returns:
            tuple[bool, str]: (success, message)
        """
        async with self._get_session() as session:
            try:
                if weather_id:
                    # Проверяем существование
                    stmt = select(model).where(model.weather_id == weather_id)  # type: ignore
                    result = await session.execute(stmt)
                    existing = result.scalar_one_or_none()

                    if existing:
                        self._lg.debug(f"Weather {weather_id} already exists.")
                        return False, f"Weather {weather_id} already exists."

                # Подготовка данных
                data = {"weather_id": weather_id}
                data.update(kwargs)

                # Создание записи
                new_weather_cache = model(**data)
                session.add(new_weather_cache)
                await session.commit()
                await session.refresh(new_weather_cache)

                # Redis cache
                await self.cache.set(key=weather_id, data=data)  # type: ignore

                self._lg.debug(f"Weather created: {new_weather_cache.weather_id}.")  # type: ignore
                return (
                    True,
                    f"Weather {new_weather_cache.weather_id} created successfully.",  # type: ignore
                )

            except Exception as e:
                await session.rollback()
                self._lg.error(f"Failed to create weather cache: {e}.", exc_info=True)
                return False, f"Error: {str(e)}."

    async def delete_weather_cache_by_id(
            self,
            model: Type[T],
            weather_id: str,
    ) -> tuple[bool, str]:
        """
        Delete weather cache by ID

        Args:
            model: Model class
            weather_id: Weather cache identifier

        Returns:
            tuple[bool, str]: (success, message)
        """
        async with self._get_session() as session:
            try:
                stmt = select(model).where(model.weather_id == weather_id)  # type: ignore
                result = await session.execute(stmt)
                weather_cache = result.scalar_one_or_none()

                if weather_cache is None:
                    self._lg.warning(f"Weather {weather_id} not found for deletion.")
                    return False, f"Weather {weather_id} not found."

                await session.delete(weather_cache)
                await session.commit()

                # Redis cache
                await self.cache.delete(key=weather_id)  # type: ignore

                self._lg.debug(f"Weather deleted: {weather_id}.")
                return True, f"Weather {weather_id} deleted successfully."

            except Exception as e:
                await session.rollback()
                self._lg.error(
                    f"Failed to delete weather cache {weather_id}: {e}.", exc_info=True
                )
                return False, f"Error: {str(e)}"

    async def find_weather_cache_by_id(
            self,
            model: Type[T],
            weather_id: str,
            as_dict: bool = True,
    ) -> T | dict[str, Any] | None:
        """
        Find weather cache by ID

        Args:
            model: Model class
            weather_id: Weather cache identifier
            as_dict: Return as dictionary instead of model instance

        Returns:
            Model instance, dictionary, or None if not found
        """
        try:
            # Проверяем кэш
            cached_data = await self.cache.get(weather_id)  # type: ignore
            if cached_data:
                return cached_data

            async with self._get_session() as session:
                stmt = select(model).where(model.weather_id == weather_id)  # type: ignore
                result = await session.execute(stmt)
                weather = result.scalar_one_or_none()

                if weather is None:
                    self._lg.debug(f"Weather {weather_id} not found.")
                    return None

                if as_dict:
                    # Преобразуем в словарь
                    result_dict = {
                        column.name: getattr(weather, column.name)
                        for column in model.__table__.columns
                    }
                    self._lg.debug(f"Weather {weather_id} found and returned as dict.")
                    return result_dict
                else:
                    # Делаем transient
                    from sqlalchemy.orm import make_transient

                    make_transient(weather)
                    self._lg.debug(
                        f"Weather {weather_id} found and returned as object."
                    )
                    return weather

        except Exception as e:
            self._lg.error(f"Error finding weather {weather_id}: {e}.")
            return None

    async def weather_cache_exists(self, model: Type[T], weather_id: str) -> bool:
        """
        Check if weather cache exists

        Args:
            model: Model class
            weather_id: Weather cache identifier

        Returns:
            bool: True if exists, False otherwise
        """
        # Проверяем кэш
        if await self.cache.exists(weather_id):  # type: ignore
            return True

        async with self._get_session() as session:
            try:
                # Используем EXISTS
                stmt = select(exists().where(model.weather_id == weather_id))  # type: ignore
                result = await session.scalar(stmt)
                return bool(result)

            except Exception as e:
                self._lg.error(f"Error checking weather cache existence: {e}.")
                return False

    async def close(self) -> None:
        """
        Close database engine and dispose connection pool

        Should be called when shutting down the application
        """
        try:
            await self.engine.dispose()
            self._lg.debug("Database engine disposed.")
        except Exception as e:
            self._lg.error(f"Error disposing engine: {e}.")


# Главная фабрика
async def get_database_methods(
        session_factory,
        Base: Type[DeclarativeBase],
        engine: AsyncEngine,
) -> MethodsOfDatabase:
    """
    Factory function to create and initialize MethodsOfDatabase

    Args:
        session_factory: SQLAlchemy async session factory
        base: Declarative base class
        engine: Async database engine

    Returns:
        Fully initialized MethodsOfDatabase instance
    """

    db_methods = MethodsOfDatabase(session_factory, Base, engine)

    # Инициализация таблиц
    await db_methods.create_tables_and_database()

    # Инициализация кеша дб Redis
    await db_methods.initialize_cache()

    return db_methods


if __name__ == "__main__":
    """Тестирование методов базы данных"""
    import asyncio
    from common.database.core import init_database
    from common.database.models import UserAllInfo
    from common.core import setup_logging


    async def main():
        setup_logging(level="DEBUG")
        _lg = get_logger()

        _lg.debug("Testing MethodsOfDatabase:")

        # Инициализация БД
        engine, SessionLocal = await init_database()

        # Создаём экземпляр
        from common.database.core.database import Base

        dbm = await get_database_methods(SessionLocal, Base, engine)

        # Тест 1: Создание пользователя
        _lg.debug("Test 1: Creating user:")
        success, msg = await dbm.create_one_user(
            model=UserAllInfo,
            user_id=500000,
            is_bot=False,
            first_name="Shayden",
            supports_inline_queries=False,
        )
        _lg.debug(f"Result: {success} - {msg}.")

        # Тест 2: Проверка существования
        _lg.debug("Test 2: Check if user exists:")
        exists = await dbm.user_exists(UserAllInfo, 5080080714)
        _lg.debug(f"User exists: {exists}.")

        # Тест 3: Поиск пользователя
        _lg.debug("Test 3: Find user:")
        user = await dbm.find_by_one_user_id(UserAllInfo, 5080080714, as_dict=True)
        _lg.debug(f"Found user: {user}.")

        # Тест 4: Обновление
        _lg.debug("Test 4: Update user:")
        success, msg, changes = await dbm.update_one_user_by_id(
            UserAllInfo, 5080080714, is_premium=True, city="Moscow"
        )
        _lg.debug(f"Result: {success} - {msg}.")
        _lg.debug(f"Changes: {changes}.")

        # Тест 5: Подсчёт
        _lg.debug("Test 5: Count users:")
        count = await dbm.count_users(UserAllInfo)
        _lg.debug(f"Total users: {count}.")

        # Закрываем соединение
        await dbm.close()

        _lg.debug("Testing completed!")


    asyncio.run(main())
