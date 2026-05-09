from typing import Any, Dict

from common.database.models import WeatherAllInfo
from common.database.repositories.base import BaseRepository
from common.utils import MethodsOfDatabase


class WeatherRepository(BaseRepository[WeatherAllInfo]):
    """Repository for WeatherAllInfo entities."""

    def __init__(self, db_methods: MethodsOfDatabase):
        super().__init__(db_methods, WeatherAllInfo)

    async def get_by_id(self, entity_id: str) -> Dict[str, Any] | None:
        """Get weather cache by ID."""
        return await self.db_methods.find_weather_cache_by_id(
            model=self.model, weather_id=entity_id, as_dict=True
        )

    async def save(self, entity_data: Dict[str, Any]) -> bool:
        """Save new weather cache."""
        success, _ = await self.db_methods.create_weather_cache(
            model=self.model, **entity_data
        )
        return success

    async def save_from_weather_id(self, weather_id, **kwargs: Any) -> bool:
        """Save new weather cache from weather_id."""
        success, _ = await self.db_methods.create_weather_cache(
            model=self.model, weather_id=weather_id, **kwargs
        )
        return success

    async def update(self, entity_id: Any, updates: Dict[str, Any]) -> bool:
        return await super().update(entity_id, updates)

    async def delete(self, entity_id: str):
        """Delete weather cache."""
        success, _ = await self.db_methods.delete_weather_cache_by_id(
            model=self.model, weather_id=entity_id
        )
        return success, _

    async def exists(self, entity_id: str) -> bool:
        """Check if weather cache exists."""
        return await self.db_methods.weather_cache_exists(
            model=self.model, weather_id=entity_id
        )
