import sys
from pathlib import Path
from typing import Any

# Для прямого запуска файла
if __name__ == "__main__":
    # Добавляем bot/ в sys.path
    bot_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(bot_dir))

import asyncio

from fluentogram import TranslatorRunner

from bot.src.core import get_logger
from bot.src.services import get_cord_from_city
from bot.src.utils import get_raw_link_api, req_data, settings

_lg = get_logger(__name__)


async def vsc_get_weather_now(
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
        if city is not None and latitude is None and longitude is None:
            cord = await get_cord_from_city(name_city=city)

            latitude = cord.get("lat", None)
            longitude = cord.get("lon", None)

            if latitude is None or longitude is None:
                _lg.warning(
                    f"Latitude: {latitude}, and Longitude: {longitude}. Error request get_cord_from_city."
                )

        url = await get_raw_link_api(
            api_name="VisualCrossing",
            latitude=latitude,
            longitude=longitude,
        )

        if url is None:
            return None

        params = {
            "key": settings.VISUAL_CROSSING_KEY,
            "unitGroup": "metric",
            "include": "current",
            "contentType": "flatjson",
        }

        req_res = await req_data(url=url, params=params)

        if locale is None:
            ERROR = "❌ Ошибка: не удалось получить данные от сервиса."  # ! Для теста
        else:
            ERROR = (
                locale.message_service_error_not_found_in_service()
            )  # ! Для теста без locale, locale=None

        current_values = req_res.get("currentConditions", ERROR)

        raw_time = current_values.get("datetime", None)
        if raw_time is None:
            time = ERROR
        time = raw_time[:5]
        raw_is_day = current_values.get("is_day", None)
        if raw_is_day is None:
            is_day = ERROR
        else:
            is_day = bool(raw_is_day)
        feels_like = round(current_values.get("feelslike", ERROR))
        temp = round(current_values.get("temp", ERROR))
        temp_unit = "°C"
        wind = round(current_values.get("windspeed", ERROR))
        wind_unit = "m/s"
        weather_code = current_values.get("weather_code", ERROR)
        humidity = round(current_values.get("humidity", ERROR))
        humidity_unit = "%"

        _lg.debug(f"Req_res is - {req_res}.")
        _lg.debug(f"Raw_time is - {raw_time}.")
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


async def vsc_get_weather_hours(
    locale: TranslatorRunner | None,
    city: str | None = None,
    latitude: str | float | None = None,
    longitude: str | float | None = None,
) -> list[dict[str, Any]] | None:
    """
    Парсит почасовой прогноз из VisualCrossing и возвращает список словарей,
    совместимый с форматом Google и WeatherAPI.
    """
    try:
        # Определение координат
        if city is not None and latitude is None and longitude is None:
            cord = await get_cord_from_city(name_city=city)
            latitude = cord.get("lat")
            longitude = cord.get("lon")

            if latitude is None or longitude is None:
                _lg.warning(f"Ошибка координат VC для города: {city}")
                return None

        url = await get_raw_link_api(
            api_name="VisualCrossing",
            latitude=latitude,
            longitude=longitude,
        )

        if url is None:
            return None

        # В параметрах обязательно unitGroup=metric для Цельсиев
        params = {
            "key": settings.VISUAL_CROSSING_KEY,
            "unitGroup": "metric",
            "include": "hours",
            "contentType": "json",  # VC лучше отдает иерархию в json, чем в flatjson для часов
        }

        req_res = await req_data(url=url, params=params)

        if not req_res or "days" not in req_res:
            _lg.error("VisualCrossing не вернул данные (days)")
            return None

        # Берем первый день (сегодня) и его массив часов
        forecast_hours_raw = req_res["days"][0]["hours"]

        hourly_weather_list = []

        for hour in forecast_hours_raw:
            # VC отдает время как "13:00:00", обрезаем до "13:00"
            time_str = hour["datetime"][:5]

            temp_value = hour["temp"]
            feels_like_value = hour["feelslike"]

            # У VC нет числовых кодов как у WeatherAPI, используем поле 'icon' или 'conditions'
            # Для унификации возвращаем icon как weather_code
            weather_code = hour.get("icon", "unknown")

            hourly_weather_list.append(
                {
                    "time": time_str,
                    "temp": round(temp_value),
                    "temp_unit": "°C",
                    "feels_like": round(feels_like_value),
                    "weather_code": weather_code,
                }
            )

        return hourly_weather_list

    except Exception as e:
        _lg.error(f"Internal error in vsc_get_weather_hours: {e}")


if __name__ == "__main__":

    async def main():
        from bot.src.core import setup_logging

        setup_logging(level="DEBUG")

        latitude = 51.73733
        longitude = 36.18735

        VisualCrossing_data = await vsc_get_weather_now(
            locale=None,
            latitude=latitude,
            longitude=longitude,
        )

        all_data: dict = {
            "VisualCrossing": VisualCrossing_data,
        }

        _lg.debug(f"All_data is - {all_data}")

        hours = await vsc_get_weather_hours(
            locale=None,
            latitude=latitude,
            longitude=longitude,
        )

        _lg.debug(f"Hours is - {hours}")

    asyncio.run(main())
