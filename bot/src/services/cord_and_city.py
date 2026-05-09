import sys
from pathlib import Path

from bot.src.utils.headers import headers_factory

# Для прямого запуска файла
if __name__ == "__main__":
    # Добавляем bot/ в sys.path
    bot_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(bot_dir))

import asyncio

import aiohttp

from common.core import get_logger
from bot.src.utils import (
    Language,
    req_data,
    get_raw_link_api,
    get_soup,
    headers_factory,
    parse_data,
)

_lg = get_logger(__name__)


# NominatimAPI
async def get_city_from_cord(
    latitude: str | float,
    longitude: str | float,
) -> str | None:
    """
    Get city name from coordinates using Nominatim reverse geocoding.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        user_agent: User-Agent header value

    Returns:
        str | None: City name or None if request failed
    """
    try:
        _lg.debug(f"Requesting city name for coordinates: {latitude}, {longitude}")

        url = await get_raw_link_api(api_name="Nominatim")
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "zoom": 10,
            "addressdetails": 1,
        }

        headers = await headers_factory(
            lang=Language.RU,
            is_api=True,
        )

        data = await req_data(url, params, headers)  # type: ignore
        address = data.get("address")

        # Try to get city name in order of priority
        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("municipality")
            or address.get("county")
        )

        if city:
            _lg.debug(f"City found: {city}")
        else:
            _lg.warning(f"No city found for coordinates: {latitude}, {longitude}")

        return city

    except asyncio.TimeoutError:
        _lg.error("Nominatim API request timeout")
        return None
    except aiohttp.ClientError as e:
        _lg.error(f"Request error: {e}")
        return None
    except ValueError as e:
        _lg.error(f"Error parsing JSON response: {e}")
        return None
    except (KeyError, AttributeError) as e:
        _lg.error(f"Error accessing response data: {e}")
        return None
    except Exception as e:
        _lg.error(f"Unexpected error: {e}")
        return None


# GeocodingAPI
async def get_cord_from_city(name_city: str | None) -> dict[str, str] | None:
    """
    Get coordinates from city name using Open-Meteo API

    Args:
        name_city: City name to search

    Returns:
        dict | None: Dictionary with 'lat' and 'lon' keys or None if error
    """
    try:
        _lg.debug(f"Getting coordinates for city: {name_city}")

        url = await get_raw_link_api(api_name="Geocoding")
        params = {
            "name": f"{name_city}",
            "language": "ru",
            "format": "json",
        }

        headers = await headers_factory(
            lang=Language.RU,
            is_api=True,
        )

        data = await req_data(url, params, headers)  # type: ignore

        if data is None:
            return None

        result = data["results"][0]
        lat = str(result.get("latitude"))
        lon = str(result.get("longitude"))

        cord = {"lat": lat, "lon": lon}

        _lg.debug(f"Retrieved coordinates for {name_city}: {cord}")
        return cord

    except (ValueError, TypeError):
        _lg.warning(f"Invalid coordinate values for city: {name_city}")
        return None
    except asyncio.TimeoutError:
        _lg.error("Request timeout")
        return None
    except aiohttp.ClientError as e:
        _lg.error(f"Request error: {e}")
        return None
    except (KeyError, IndexError, TypeError) as e:
        _lg.error(f"Error parsing API response: {e}")
        return None
    except Exception as e:
        _lg.error(f"Internal error: {e}")
        return None


if __name__ == "__main__":

    async def main():
        from common.core import setup_logging

        setup_logging(level="DEBUG")

        # NominatimAPI
        lat, lon = 51.705684, 36.164215  # Kursk coordinates
        city = await get_city_from_cord(lat, lon)
        _lg.debug(f"City: {city}")

        # GeocodingAPI
        # Test with valid city
        result = await get_cord_from_city("Москва")
        _lg.debug(f"Result: {result}")

        # Test with invalid city
        result = await get_cord_from_city("InvalidCityXYZ123")
        _lg.debug(f"Result: {result}")

    asyncio.run(main())
