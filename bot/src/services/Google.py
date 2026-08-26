import sys
from pathlib import Path

# Для прямого запуска файла
if __name__ == "__main__":
    # Добавляем bot/ в sys.path
    bot_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(bot_dir))

import asyncio

from fluentogram import TranslatorRunner

from common.core import get_logger
from common.utils import settings
from bot.src.services import get_cord_from_city
from bot.src.utils import get_raw_link_api, req_data

_lg = get_logger(__name__)


async def goo_get_weather_now(
    locale: TranslatorRunner | None,
    city: str | None = None,
    latitude: str | float | None = None,
    longitude: str | float | None = None,
) -> dict[str, dict[str, str | bool | None]] | None:
    """
    Locale = None ONLY for test. \n
    Needed city or lat and lon.
    """
    try:
        url = await get_raw_link_api(api_name="Google")

        if url is None:
            return None

        url = url.replace("{forecast}", "currentConditions")

        if city is not None and latitude is None and longitude is None:
            cord = await get_cord_from_city(name_city=city)

            latitude = cord.get("lat", None)
            longitude = cord.get("lon", None)

            if latitude is None or longitude is None:
                _lg.warning(
                    f"Latitude: {latitude}, and Longitude: {longitude}. Error request get_cord_from_city."
                )

        params = {
            "key": settings.GOOGLE_KEY,
            "location.latitude": latitude,
            "location.longitude": longitude,
            "unitsSystem": "METRIC",  # TODO
            "languageCode": "ru",  # TODO
        }

        req_res = await req_data(url=url, params=params)

        if locale is None:
            ERROR = "❌ Ошибка: не удалось получить данные от сервиса."  # ! Для теста
        else:
            ERROR = (
                locale.message_service_error_not_found_in_service()
            )  # ! Для теста без locale, locale=None

        time = req_res.get("currentTime", ERROR)[11:16]
        is_day = req_res.get("isDaytime", ERROR)
        feels_like = round(
            req_res.get("feelsLikeTemperature", ERROR).get("degrees", ERROR)
        )
        temp = round(req_res.get("temperature", ERROR).get("degrees", ERROR))
        temp_unit = req_res.get("temperature", ERROR).get("unit", ERROR)
        wind = round(
            req_res.get("wind", ERROR).get("speed", ERROR).get("value", ERROR) / 3.6
        )
        wind_unit = "m/s"
        weather_code = (
            req_res.get("weatherCondition", ERROR)
            .get("description", ERROR)
            .get("text", ERROR)
        )
        humidity = round(req_res.get("relativeHumidity", ERROR))
        humidity_unit = "%"  # ! Только проценты

        _lg.debug(f"Req_res is - {req_res}.")
        _lg.debug(f"Time is - {time}.")
        _lg.debug(f"Is_day is - {is_day}.")
        _lg.debug(f"Feels_like is - {feels_like}.")
        _lg.debug(f"Temp is - {temp}.")
        _lg.debug(f"Temp_unit is - {temp_unit}.")
        _lg.debug(f"Wind is - {wind}.")
        _lg.debug(f"Wind_unit is - {wind_unit}.")
        _lg.debug(f"Weather_code is - {weather_code}.")
        _lg.debug(f"Humidity is - {humidity}.")
        _lg.debug(f"Humidity_unit is - {humidity_unit}.")

        current_weather_dict = {
            "time": time,
            "is_day": is_day,
            "feels_like": feels_like,
            "temp": temp,
            "temp_unit": temp_unit,
            "wind": wind,
            "wind_unit": wind_unit,
            "weather_code": weather_code,
            "humidity": humidity,
            "humidity_unit": humidity_unit,
        }

        _lg.debug(f"Current_weather_dict is - {current_weather_dict}.")

        return current_weather_dict

    except Exception as e:
        _lg.error(f"Internal error: {e}")


async def goo_get_weather_hours(
    locale: TranslatorRunner | None,
    city: str | None = None,
    latitude: str | float | None = None,
    longitude: str | float | None = None,
):
    """
    Locale = None ONLY for test. \n
    Needed city or lat and lon.
    """
    try:
        url = await get_raw_link_api(api_name="Google")

        if url is None:
            return None

        url = url.replace("{forecast}", "forecast/hours")

        if city is not None and latitude is None and longitude is None:
            cord = await get_cord_from_city(name_city=city)

            latitude = cord.get("lat", None)
            longitude = cord.get("lon", None)

            if latitude is None or longitude is None:
                _lg.warning(
                    f"Latitude: {latitude}, and Longitude: {longitude}. Error request get_cord_from_city."
                )

        params = {
            "key": settings.GOOGLE_KEY,
            "location.latitude": latitude,
            "location.longitude": longitude,
            "hours": 24,
            "pageSize": 24,
            "unitsSystem": "METRIC",  # TODO
            "languageCode": "ru",  # TODO
        }

        req_res = await req_data(url=url, params=params)

        if locale is None:
            ERROR = "❌ Ошибка: не удалось получить данные от сервиса."  # ! Для теста
        else:
            ERROR = (
                locale.message_service_error_not_found_in_service()
            )  # ! Для теста без locale, locale=None

        forecast_hours = req_res.get("forecastHours", ERROR)

        hourly_weather_list = []

        for hour in forecast_hours:
            h = hour["displayDateTime"]["hours"]
            time_str = f"{h:02d}:00"
            temp_value = hour["temperature"]["degrees"]
            temp_unit = "°C" if hour["temperature"]["unit"] == "CELSIUS" else "°F"
            feels_like_value = hour["feelsLikeTemperature"]["degrees"]
            weather_code = hour["weatherCondition"]["type"]

            # Формируем словарь для текущего часа
            hourly_weather_list.append(
                {
                    "time": time_str,
                    "temp": round(temp_value),
                    "temp_unit": temp_unit,
                    "feels_like": round(feels_like_value),
                    "weather_code": weather_code,
                }
            )

        return hourly_weather_list

    except Exception as e:
        _lg.error(f"Internal error: {e}")


if __name__ == "__main__":

    async def main():
        from common.core import setup_logging

        setup_logging(level="DEBUG")

        latitude = 51.73733
        longitude = 36.18735

        Google_data = await goo_get_weather_now(
            locale=None,
            latitude=latitude,
            longitude=longitude,
        )

        all_data: dict = {
            "Google": Google_data,
        }

        _lg.debug(f"All_data is - {bool(all_data)}")

        hours = await goo_get_weather_hours(
            locale=None,
            latitude=latitude,
            longitude=longitude,
        )

        _lg.debug(f"Hours is - {hours}")

    asyncio.run(main())
