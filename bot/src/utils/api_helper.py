import asyncio
import sys
from pathlib import Path
from typing import Any

# Для прямого запуска файла
if __name__ == "__main__":
    # Добавляем bot/ в sys.path
    bot_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(bot_dir))

import aiohttp

from common.core import get_logger

_lg = get_logger(__name__)


async def get_raw_link_api(
    latitude: str | float | None = None,
    longitude: str | float | None = None,
    api_name: str | None = None,
    srv_and_links: dict[str, str] = {
        "OpenMeteo": "https://api.open-meteo.com/v1/forecast?",
        "VisualCrossing": "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat}%2C%20{lon}?",
        "WeatherAPI": "https://api.weatherapi.com/v1/{forecast}.json?",
        "YandexParser": "https://yandex.ru/pogoda/{lang}?",
        "Nominatim": "https://nominatim.openstreetmap.org/reverse",
        "Geocoding": "https://geocoding-api.open-meteo.com/v1/search?",
        "Google": "https://weather.googleapis.com/v1/{forecast}:lookup?",
    },
) -> dict[str, str] | str | None:
    """
    Returns dict with raw key and links. \n
    Lat and Lon needed only with use VisualCrossing. \n
    If api_name is None return all srv_and_links. \n
    """
    try:
        for key in srv_and_links:
            value = (
                srv_and_links.get(key, None)
                .replace("{lat}", str(latitude))
                .replace("{lon}", str(longitude))
            )

            srv_and_links.update({key: value})

        if api_name is None:
            return srv_and_links

        return srv_and_links[api_name]

    except Exception as e:
        _lg.error(f"Internal error: {e}")


async def req_data(
    url: str | dict,
    params: dict,
    headers: dict | None = None,
) -> Any | None:
    """Request data from api."""
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(
                url,  # type: ignore
                headers=headers,
                params=params,
            ) as response:  # headers=headers
                response.raise_for_status()
                data = await response.json()

                return data

    except asyncio.TimeoutError as e:
        _lg.error(f"API request timeout: {e}")
    except aiohttp.ClientError as e:
        _lg.error(f"Request error: {e}")
    except ValueError as e:
        _lg.error(f"Error parsing JSON response: {e}")
    except Exception as e:
        _lg.error(f"Internal error: {e}")


if __name__ == "__main__":
    import asyncio

    async def main():
        from common.core import setup_logging

        setup_logging(level="DEBUG")

        # 1 get_raw_link_api
        result1 = await get_raw_link_api(
            latitude=51.2222,
            longitude=52.312313,
        )
        _lg.debug(f"get_raw_link_api result is - {result1}")

        # 2 req_data
        lat = 51.73733
        lon = 36.18735
        # OpenMeteo Par
        res2_url = result1["OpenMeteo"]  # type: ignore
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m",
                "apparent_temperature",
                "is_day",
                "relative_humidity_2m",
                "weather_code",
                "cloud_cover",
                "wind_speed_10m",
            ],
            "timezone": "auto",
        }
        result2 = await req_data(res2_url, params)
        _lg.debug(f"req_data openmeteo result is - {result2}")

        # VisualCrossing Par
        res2_url = (
            result1["VisualCrossing"]  # type: ignore
            .replace("{lat}", str(lat))
            .replace("{lon}", str(lon))
        )
        params = {
            "unitGroup": "metric",
            "include": "current",
            "contentType": "flatjson",
        }
        result2 = await req_data(res2_url, params)
        _lg.debug(f"req_data visualcrossing result is - {result2}")

        # Nominatim Par # TODO NOMINATIM не работает
        res2_url = result1["Nominatim"]  # type: ignore
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 10,
            "addressdetails": 1,
        }
        result2 = await req_data(res2_url, params)
        _lg.debug(f"req_data nominatim result is - {result2}")

        # Geocoding Par
        res2_url = result1["Geocoding"]  # type: ignore
        params = {
            "name": "Курск",
            "language": "ru",
            "format": "json",
        }
        result2 = await req_data(res2_url, params)
        _lg.debug(f"req_data geocoding result is - {result2}")

    asyncio.run(main())
