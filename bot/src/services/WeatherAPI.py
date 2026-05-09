from datetime import datetime
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

from common.core import get_logger
from bot.src.services import get_cord_from_city
from bot.src.utils import get_raw_link_api, req_data, settings

_lg = get_logger(__name__)


async def wapi_get_weather_now(
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
        url = await get_raw_link_api(api_name="WeatherAPI")

        if url is None:
            return None

        url = url.replace("{forecast}", "current")

        if city is not None and latitude is None and longitude is None:
            cord = await get_cord_from_city(name_city=city)

            latitude = cord.get("lat", None)
            longitude = cord.get("lon", None)

            if latitude is None or longitude is None:
                _lg.warning(
                    f"Latitude: {latitude}, and Longitude: {longitude}. Error request get_cord_from_city."
                )

        params = {
            "key": settings.WEATHER_API_KEY,
            "q": f"{latitude},{longitude}",
        }

        req_res = await req_data(url=url, params=params)

        if locale is None:
            ERROR = "❌ Ошибка: не удалось получить данные от сервиса."  # ! Для теста
        else:
            ERROR = (
                locale.message_service_error_not_found_in_service()
            )  # ! Для теста без locale, locale=None

        current_values = req_res.get("current", ERROR)
        current_condition = current_values.get("condition", ERROR)

        raw_time = current_values.get("last_updated", None)
        if raw_time is None:
            time = ERROR
        time = raw_time[11:]
        is_day = bool(current_values.get("is_day", ERROR))
        feels_like = round(current_values.get("feelslike_c", ERROR))
        temp = round(current_values.get("temp_c", ERROR))
        temp_unit = "°C"
        wind_kph = round(current_values.get("wind_kph", ERROR))
        wind_mps = round(wind_kph / 3.6)
        wind = wind_mps
        wind_unit = "m/s"
        weather_code = current_condition.get("code", ERROR)
        humidity = round(current_values.get("humidity", ERROR))
        humidity_unit = "%"

        _lg.debug(f"Req_res is - {req_res}.")
        _lg.debug(f"Raw_time is - {raw_time}.")
        _lg.debug(f"Time is - {time}.")
        _lg.debug(f"Is_day is - {is_day}.")
        _lg.debug(f"Feels_like is - {feels_like}.")
        _lg.debug(f"Temp is - {temp}.")
        _lg.debug(f"Temp_unit is - {temp_unit}.")
        _lg.debug(f"wind_kph is - {wind_kph}.")
        _lg.debug(f"Wind_mps is - {wind_mps}.")
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


async def wapi_get_weather_hours(
    locale: TranslatorRunner | None,
    city: str | None = None,
    latitude: str | float | None = None,
    longitude: str | float | None = None,
) -> list[dict[str, Any]] | None:
    """
    Locale = None ONLY for test. \n
    Needed city or lat and lon.
    """
    try:
        url = await get_raw_link_api(api_name="WeatherAPI")

        if url is None:
            return None

        url = url.replace("{forecast}", "forecast")

        # Определение координат
        if city is not None and latitude is None and longitude is None:
            cord = await get_cord_from_city(name_city=city)
            latitude = cord.get("lat")
            longitude = cord.get("lon")

            if latitude is None or longitude is None:
                _lg.warning(f"Ошибка получения координат для города: {city}")
                return None

        params = {
            "key": settings.WEATHER_API_KEY,
            "q": f"{latitude},{longitude}",
            "days": 1,
            "aqi": "no",
            "alerts": "no",
        }

        req_res = await req_data(url=url, params=params)

        if not req_res or "forecast" not in req_res:
            _lg.error("WeatherAPI не вернул прогноз (forecast)")
            return None

        # Достаем список часов из первого дня прогноза
        forecast_hours_raw = req_res["forecast"]["forecastday"][0]["hour"]

        hourly_weather_list = []

        for hour in forecast_hours_raw:
            # Извлекаем время (формат "2026-04-16 13:00" -> "13:00")
            time_str = hour["time"].split(" ")[1]

            temp_value = hour["temp_c"]
            feels_like_value = hour["feelslike_c"]

            # Код состояния (у WeatherAPI это числовой code, например 1003)
            weather_code = str(hour["condition"]["code"])

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
        _lg.error(f"Internal error in wapi_get_weather_hours: {e}")


async def wapi_get_weather_astro(
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
        url = await get_raw_link_api(api_name="WeatherAPI")

        if url is None:
            return None

        url = url.replace("{forecast}", "astronomy")

        if city is not None and latitude is None and longitude is None:
            cord = await get_cord_from_city(name_city=city)

            latitude = cord.get("lat", None)
            longitude = cord.get("lon", None)

            if latitude is None or longitude is None:
                _lg.warning(
                    f"Latitude: {latitude}, and Longitude: {longitude}. Error request get_cord_from_city."
                )

        params = {
            "key": settings.WEATHER_API_KEY,
            "q": f"{latitude},{longitude}",
            "dt": f"{datetime.now().strftime('%Y-%m-%d')}",
        }

        req_res = await req_data(url=url, params=params)

        if not req_res or "astronomy" not in req_res:
            return None

        astro = req_res["astronomy"]["astro"]

        # Вспомогательная функция для конвертации "05:35 AM" -> "05:35"
        def to_24h(t_str):
            try:
                return datetime.strptime(t_str, "%I:%M %p").strftime("%H:%M")
            except Exception:
                return t_str

        if locale is None:
            ERROR = "❌ Ошибка: не удалось получить данные от сервиса."  # ! Для теста
        else:
            ERROR = (
                locale.message_service_error_not_found_in_service()
            )  # ! Для теста без locale, locale=None

        # Считаем долготу дня
        # Превращаем в объекты времени для вычитания
        fmt = "%I:%M %p"
        sunrise_dt = datetime.strptime(astro["sunrise"], fmt)
        sunset_dt = datetime.strptime(astro["sunset"], fmt)
        duration = sunset_dt - sunrise_dt
        hours, remainder = divmod(duration.seconds, 3600)
        minutes = remainder // 60
        day_length = f"{hours}ч {minutes}м"

        # Формируем итоговый словарь
        result = {
            "city": city or req_res["location"]["name"],
            "sunrise": to_24h(astro["sunrise"]),
            "sunset": to_24h(astro["sunset"]),
            "day_length": day_length,
            "moon_phase": astro["moon_phase"],  # Названия фаз переведем в шаблоне
            "moon_illumination": astro["moon_illumination"],
            "moonrise": to_24h(astro["moonrise"]),
            "moonset": to_24h(astro["moonset"]),
            "is_sun_up": astro["is_sun_up"],
            # UV-индекс и видимость обычно приходят из основного прогноза (forecast),
        }

        return result

    except Exception as e:
        _lg.error(f"Internal error in wapi_get_weather_hours: {e}")


if __name__ == "__main__":

    async def main():
        from common.core import setup_logging

        setup_logging(level="DEBUG")

        latitude = 51.73733
        longitude = 36.18735

        VisualCrossing_data = await wapi_get_weather_now(
            locale=None,
            latitude=latitude,
            longitude=longitude,
        )

        all_data: dict = {
            "VisualCrossing": VisualCrossing_data,
        }

        _lg.debug(f"All_data is - {all_data}")

        hours = await wapi_get_weather_hours(
            locale=None,
            latitude=latitude,
            longitude=longitude,
        )

        _lg.debug(f"Hours is - {hours}")

        astro = await wapi_get_weather_astro(
            locale=None,
            latitude=latitude,
            longitude=longitude,
        )

        _lg.debug(f"Astro is - {astro}")

    asyncio.run(main())
