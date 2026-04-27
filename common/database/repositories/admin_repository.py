from typing import Any

from common.database.repositories.base import BaseRepository
from common.database.models import Admin


class AdminRepository(BaseRepository[Admin]):
    def __init__(self, db_methods):
        super().__init__(db_methods, Admin)

    async def is_admin(self, user_id: int) -> bool:
        return await self.db_methods.is_admin(model=self.model, user_id=user_id)

    async def add_admin(self, user_id: int) -> bool:
        return await self.db_methods.add_admin(model=self.model, user_id=user_id)

    # Заглушки для абстрактных методов
    async def get_by_id(self, entity_id: Any):
        pass

    async def save(self, entity_data: dict):
        pass

    async def update(self, entity_id, updates):
        pass

    async def delete(self, entity_id):
        pass

    async def exists(self, entity_id):
        pass
