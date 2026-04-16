"""Фикстуры для тестирования api_helper.py"""

import pytest


@pytest.fixture
def mock_successful_json_response():
    """Успешный JSON ответ"""
    return {
        "current": {
            "temperature_2m": 15.5,
            "wind_speed_10m": 5.2,
        },
        "status": "ok",
    }


@pytest.fixture
def mock_empty_json_response():
    """Пустой JSON ответ"""
    return {}
