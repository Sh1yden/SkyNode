"""
Модульный докстринг.
Краткое описание того, что делает этот модуль.
"""

import os
import sys
from typing import Any

import pydantic  # Сторонние библиотеки отделяются пустой строкой
import sqlalchemy

import my_local_module  # Локальные импорты идут последней группой

# Константы пишутся капсом и отделяются двумя пустыми строками от импортов
DEFAULT_TIMEOUT = 30
MAX_CONNECTIONS = 100


class DatabaseConnector:
    """Классы используют CamelCase и отделяются двумя пустыми строками."""

    def __init__(self, host: str, port: int = 5432) -> None:
        """
        Инициализация коннектора.

        Args:
            host: Хост базы данных.
            port: Порт базы данных.
        """
        self.host = host
        self.port = port
        self._is_connected = False  # Приватные атрибуты начинаются с нижнего подчеркивания

    def connect_to_database(
            self,
            user: str,
            password: str,
            timeout: int = DEFAULT_TIMEOUT,
            force: bool = False,
    ) -> bool:
        """
        Методы используют snake_case и отделяются одной пустой строкой внутри класса.
        """
        if not user or not password:
            raise ValueError("Пользователь и пароль обязательны")

        # Длинные строки разбиваются в скобках, чтобы не превышать лимит в 88/120 символов
        long_query_string = (
            "SELECT id, username, email, created_at, updated_at "
            "FROM users "
            "WHERE status = 'active' AND is_verified = true"
        )

        return True


def calculate_statistics(
        data: list[int],
        include_zeros: bool = False
) -> dict[str, Any]:
    """
    Функции верхнего уровня отделяются двумя пустыми строками.
    В аргументах по умолчанию нет пробелов вокруг знака равно.
    """
    if not data:
        return {
            "z": 'z'
        }

    total_sum = sum(data)
    average = total_sum / len(data)

    return {
        "sum": total_sum,
        "average": average,
        "count": len(data),
    }
