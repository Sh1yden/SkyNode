import pickle
import redis.asyncio
from typing import Any


from bot.src.core import get_logger
from bot.src.utils import settings


class RedisCache:
    """
    Async Redis cache manager for data serialization and caching operations.
    """

    def __init__(
        self,
        db: int = 0,
        decode_responses: bool = False,  # False для работы с bytes
    ):
        self._lg = get_logger()
        self._lg.debug("Initializing AsyncRedisCache.")

        self.host = settings.REDIS_HOST
        self.port = settings.REDIS_PORT

        self._lg.debug(f"=== Redis Connection Details ===")
        self._lg.debug(f"Host: {self.host}")
        self._lg.debug(f"Port: {self.port}")

        self.db = db
        self.decode_responses = decode_responses
        self.connection: redis.asyncio.Redis | None = None

    async def connect(self) -> None:
        """Connect to Redis server (async)."""
        try:
            self.connection = redis.asyncio.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=self.decode_responses,
            )
            # Проверяем соединение
            await self.connection.ping()
            self._lg.info(f"Connected to Redis at {self.host}:{self.port}")
        except Exception as e:
            self._lg.error(f"Failed to connect to Redis: {e}")
            self.connection = None

    async def close(self) -> None:
        """Close Redis connection."""
        if self.connection:
            try:
                await self.connection.aclose()
                self._lg.info("Redis connection closed")
            except Exception as e:
                self._lg.error(f"Error closing Redis connection: {e}")

    def serialize_data(self, data: Any) -> bytes | None:
        """Serialize data using pickle."""
        try:
            return pickle.dumps(data)
        except Exception as e:
            self._lg.error(f"Failed to serialize data: {e}")

    def deserialize_data(self, data: bytes | None) -> Any:
        """Deserialize data using pickle."""
        if data is None:
            return None
        try:
            return pickle.loads(data)
        except Exception as e:
            self._lg.error(f"Failed to deserialize data: {e}")
            return None

    async def set(self, key: Any, data: Any, ex: int | None = None) -> None:
        """
        Cache data in Redis.

        Args:
            key: Cache key
            data: Data to cache
            ex: Expiration time in seconds (optional)
        """
        if self.connection is None:
            self._lg.warning("Redis connection not established")
            return

        try:
            serialized = self.serialize_data(data)
            await self.connection.set(key, serialized, ex=ex)
            self._lg.debug(f"Successfully cached data for key: {key}")
        except Exception as e:
            self._lg.error(f"Failed to cache data for key {key}: {e}")

    async def get(self, key: Any) -> Any:
        """Get cached data from Redis."""
        if self.connection is None:
            self._lg.warning("Redis connection not established")
            return None

        try:
            cached_data = await self.connection.get(key)
            if cached_data and isinstance(cached_data, bytes):
                self._lg.debug(f"Successfully retrieved cached data for key: {key}")
                return self.deserialize_data(cached_data)
            else:
                self._lg.debug(f"No cached data found for key: {key}")
                return None
        except Exception as e:
            self._lg.error(f"Failed to get cached data for key {key}: {e}")
            return None

    async def update(self, key: Any, updated_fields: dict[str, dict]) -> None:
        """
        Update specific fields in cached data.

        Args:
            key: Cache key
            updated_fields: Dict of {field: {"old": value, "new": value}}
        """
        if self.connection is None:
            self._lg.warning("Redis connection not established")
            return

        try:
            cached_data = await self.get(key)
            if cached_data is None:
                cached_data = {}

            for field, changes in updated_fields.items():
                cached_data[field] = changes["new"]

            await self.set(key, cached_data)
            self._lg.debug(
                f"Updated cache for key {key}: {list(updated_fields.keys())}"
            )
        except Exception as e:
            self._lg.error(f"Failed to update cache for key {key}: {e}")

    async def delete(self, key: Any) -> None:
        """Delete cached data."""
        if self.connection is None:
            self._lg.warning("Redis connection not established")
            return

        try:
            await self.connection.delete(key)
            self._lg.debug(f"Successfully deleted cached data for key: {key}")
        except Exception as e:
            self._lg.error(f"Failed to delete cached data for key {key}: {e}")

    async def exists(self, key: Any) -> bool:
        """Check if key exists in cache."""
        if self.connection is None:
            self._lg.warning("Redis connection not established")
            return False

        try:
            result = await self.connection.exists(key)
            return bool(result)
        except Exception as e:
            self._lg.error(f"Failed to check existence for key {key}: {e}")
            return False
