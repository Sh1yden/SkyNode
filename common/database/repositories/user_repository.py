from typing import Any, Dict

from aiogram.types import User

from common.database.models import UserAllInfo
from common.database.repositories.base import BaseRepository
from bot.src.utils.db_utils import MethodsOfDatabase


class UserRepository(BaseRepository[UserAllInfo]):
    """Repository for UserAllInfo entities."""

    def __init__(self, db_methods: MethodsOfDatabase):
        super().__init__(db_methods, UserAllInfo)

    async def get_by_id(self, entity_id: int) -> Dict[str, Any] | None:
        """Get user by ID."""
        return await self.db_methods.find_by_one_user_id(
            model=self.model, user_id=entity_id, as_dict=True
        )

    async def save(self, entity_data: Dict[str, Any] = {}, **kwargs: Any):
        """Save new user."""
        success, msg = await self.db_methods.create_one_user(
            model=self.model, **entity_data, **kwargs
        )
        return success, msg

    async def save_from_telegram_user(self, user: User, **kwargs: Any) -> bool:
        """Save user from Telegram User object."""
        success, _ = await self.db_methods.create_one_user(
            model=self.model, user=user, **kwargs
        )
        return success

    async def update(self, entity_id: int, updates: Dict[str, Any]):
        """Update user."""
        success, msg, upd_field = await self.db_methods.update_one_user_by_id(
            model=self.model, user_id=entity_id, **updates
        )
        return success, msg, upd_field

    async def delete(self, entity_id: int):
        """Delete user."""
        success, msg = await self.db_methods.delete_one_user_by_id(
            model=self.model, user_id=entity_id
        )
        return success, msg

    async def exists(self, entity_id: int) -> bool:
        """Check if user exists."""
        return await self.db_methods.user_exists(model=self.model, user_id=entity_id)

    async def has_location(self, user_id: int) -> bool:
        """Check if user has location data."""
        return await self.db_methods.user_location_exists(
            model=self.model, user_id=user_id
        )

    async def update_location(
        self,
        user_id: int,
        city: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> bool:
        """Update user location."""
        updates = {}
        if city is not None:
            updates["city"] = city
        if latitude is not None:
            updates["latitude"] = latitude
        if longitude is not None:
            updates["longitude"] = longitude
        return await self.update(user_id, updates)

    async def get_all_user_ids(
        self,
        limit: int | None,
        offset: int | None,
    ) -> list[int]:
        """Get all user IDs."""
        return await self.db_methods.get_all_user_ids(
            model=self.model,
            limit=limit,
            offset=offset,
        )
