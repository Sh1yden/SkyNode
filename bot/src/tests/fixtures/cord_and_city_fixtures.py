"""Фикстуры для тестирования cord_and_city.py"""

import pytest


@pytest.fixture
def mock_successful_nominatim_response():
    """Успешный ответ от Nominatim API"""
    return {
        "address": {
            "city": "Moscow",
            "town": None,
            "village": None,
            "municipality": None,
            "county": None,
        }
    }


@pytest.fixture
def mock_nominatim_response_with_town():
    """Ответ Nominatim с town вместо city"""
    return {
        "address": {
            "city": None,
            "town": "Kursk",
            "village": None,
            "municipality": None,
            "county": None,
        }
    }


@pytest.fixture
def mock_nominatim_response_with_village():
    """Ответ Nominatim с village"""
    return {
        "address": {
            "city": None,
            "town": None,
            "village": "Ivanovka",
            "municipality": None,
            "county": None,
        }
    }


@pytest.fixture
def mock_nominatim_response_with_municipality():
    """Ответ Nominatim с municipality"""
    return {
        "address": {
            "city": None,
            "town": None,
            "village": None,
            "municipality": "District Center",
            "county": None,
        }
    }


@pytest.fixture
def mock_nominatim_response_with_county():
    """Ответ Nominatim с county"""
    return {
        "address": {
            "city": None,
            "town": None,
            "village": None,
            "municipality": None,
            "county": "Oblast",
        }
    }


@pytest.fixture
def mock_nominatim_response_no_city():
    """Ответ Nominatim без города"""
    return {"address": {}}


@pytest.fixture
def mock_successful_geocoding_response():
    """Успешный ответ от Geocoding API"""
    return {
        "results": [
            {
                "latitude": 55.7558,
                "longitude": 37.6173,
            }
        ]
    }


@pytest.fixture
def mock_empty_geocoding_response():
    """Пустой ответ от Geocoding API"""
    return {"results": []}


@pytest.fixture
def mock_geocoding_response_no_results():
    """Ответ Geocoding без results"""
    return {}
