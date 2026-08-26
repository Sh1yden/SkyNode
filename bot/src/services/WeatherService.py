from io import BytesIO
import sys
from pathlib import Path

# Для прямого запуска файла
if __name__ == "__main__":
    # Добавляем bot/ в sys.path
    bot_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(bot_dir))

import asyncio
from datetime import datetime, timedelta

from fluentogram import TranslatorRunner

from common.core import get_logger

# utils
from bot.src.utils import generate_hourly_forecast_image

# cord
from bot.src.services import (
    get_city_from_cord,
    get_cord_from_city,
)

# now
from bot.src.services import (
    opm_get_weather_now,
    vsc_get_weather_now,
    wapi_get_weather_now,
    yan_get_weather_now,
    goo_get_weather_now,
)

# hours
from bot.src.services import (
    yan_get_weather_hours,
    opm_get_weather_hours,
    goo_get_weather_hours,
    wapi_get_weather_hours,
    vsc_get_weather_hours,
)

from bot.src.services import wapi_get_weather_astro

_lg = get_logger()

# TODO когда то сделать переключение с м/с на км/ч и тд


async def aggregated_weather(
    results: dict,
    priority_order: list[str] = [
        "YandexParser",
        "OpenMeteo",
        "Google",
        "WeatherAPI",
        "VisualCrossing",
    ],
) -> tuple[dict, list] | None:
    """Aggregate by priority."""
    try:
        aggregated = {}
        sources = []
        for api_name in priority_order:
            if api_name in results:
                data = results[api_name]
                if data and not isinstance(data, Exception):
                    sources.append(api_name)
                    for key, value in data.items():
                        if key not in aggregated and value not in [
                            None,
                            "ERROR",
                            "❌ Ошибка: не удалось получить данные от сервиса.",
                        ]:
                            aggregated[key] = value

        return aggregated, sources

    except Exception as e:
        _lg.error(f"Internal error: {e}")


async def avg_and_filtered_temp(sources, results: dict) -> tuple[int, int] | None:
    """Filter and"""
    try:
        temps = []
        for api_name in sources:
            if (
                api_name in results
                and results[api_name]
                and "temp" in results[api_name]
            ):
                temp_val = results[api_name]["temp"]
                if temp_val is not None:  # TODO улучшить фильтрацию
                    try:
                        temps.append(float(temp_val))
                    except ValueError as e:
                        _lg.error(f"ValueError: {e}")

        avg_temp = round(sum(temps) / len(temps) if temps else 0)
        avg_filtered = round(avg_temp)  # ! Пока без фильтрации

        return avg_temp, avg_filtered

    except Exception as e:
        _lg.error(f"Internal error: {e}")


async def decode_weather_code(locale: TranslatorRunner, code: int) -> str:
    # TODO i18n добавить
    WEATHER_CODES = {
        404: locale.message_service_error_not_found_in_service(),
        0: "Ясно",
        1: "Преимущественно ясно",
        2: "Переменная облачность",
        3: "Пасмурно",
        45: "Туман",
        48: "Инейный туман",
        51: "Морось слабая",
        53: "Морось умеренная",
        55: "Морось сильная",
        56: "Ледяная морось слабая",
        57: "Ледяная морось сильная",
        61: "Дождь слабый",
        63: "Дождь умеренный",
        65: "Дождь сильный",
        66: "Ледяной дождь слабый",
        67: "Ледяной дождь сильный",
        71: "Снег слабый",
        73: "Снег умеренный",
        75: "Снег сильный",
        77: "Снежные зерна",
        80: "Ливень слабый",
        81: "Ливень умеренный",
        82: "Ливень сильный",
        85: "Снежный ливень слабый",
        86: "Снежный ливень сильный",
        95: "Гроза слабая",
        96: "Гроза с градом",
        99: "Гроза сильная с градом",
    }
    return WEATHER_CODES.get(code, f"{code}")


async def connect_templates(
    locale: TranslatorRunner, results: dict, sources, temp_unit
):
    try:
        ERROR = locale.message_service_error_not_found_in_service()

        sources_text = ""
        for i, source_name in enumerate(sources, 1):
            data = results[source_name]
            temp = data.get("temp", ERROR)
            sources_text += (
                locale.message_weather_now_source_template(
                    num=i, source_name=source_name, temp=temp, temp_unit=temp_unit
                )
                + "\n"
            )

            # Summary
            weather_code = data.get("weather_code", 404)
            condition = await decode_weather_code(locale=locale, code=weather_code)
            feels_like = data.get("feels_like", temp)
            humidity = data.get("humidity", ERROR)
            humidity_unit = data.get("humidity_unit", ERROR)
            wind = data.get("wind", ERROR)
            wind_unit = data.get("wind_unit", ERROR)

            sources_text += (
                locale.message_weather_now_summary_template(
                    condition=condition,
                    feels_like=feels_like,
                    temp_unit=temp_unit,
                    humidity=humidity,
                    humidity_unit=humidity_unit,
                    wind=wind,
                    wind_unit=wind_unit,
                )
                + "\n"
            ) + "\n"

        return sources_text

    except Exception as e:
        _lg.error(f"Internal error: {e}")


async def get_weather_now(
    locale: TranslatorRunner,
    weather_repo,
    city: str | None = None,
    latitude: str | float | None = None,
    longitude: str | float | None = None,
    usr_loc: dict[str, str] | None = None,
) -> str | None:
    """Get now weather forecast"""
    try:
        if usr_loc is not None:
            latitude = usr_loc.get("latitude", None)
            longitude = usr_loc.get("longitude", None)

        if city is not None and latitude is None and longitude is None:
            cord = await get_cord_from_city(name_city=city)

            latitude = cord.get("lat", None)
            longitude = cord.get("lon", None)

        if city is None and latitude and longitude:
            city = await get_city_from_cord(latitude=latitude, longitude=longitude)

        if latitude is None or longitude is None:
            _lg.error(f"Latitude: {latitude}, and Longitude: {longitude}. Error!")
            return None

        ymdhm = datetime.now().strftime("%Y%m%d%H")
        weather_id = f"now_{city}{ymdhm}"

        # Redis cache
        if await weather_repo.exists(weather_id):
            weather_now_msg = await weather_repo.get_by_id(weather_id)
            return weather_now_msg["weather_now_msg"]

        else:
            results = {}
            # ! Расположены в порядке сортировки
            # YandexParser
            results["YandexParser"] = await yan_get_weather_now(
                locale=locale,
                latitude=latitude,
                longitude=longitude,
            )

            # OpenMeteo
            results["OpenMeteo"] = await opm_get_weather_now(
                locale=locale,
                latitude=latitude,
                longitude=longitude,
            )

            # Google
            results["Google"] = await goo_get_weather_now(
                locale=locale,
                latitude=latitude,
                longitude=longitude,
            )

            # WeatherAPI
            results["WeatherAPI"] = await wapi_get_weather_now(
                locale=locale,
                latitude=latitude,
                longitude=longitude,
            )

            # VisualCrossing
            results["VisualCrossing"] = await vsc_get_weather_now(
                locale=locale,
                latitude=latitude,
                longitude=longitude,
            )

            _lg.debug(f"Results is - {results}")

            aggregated, sources = await aggregated_weather(results=results)

            ERROR = locale.message_service_error_not_found_in_service()

            temp_unit = aggregated.get("temp_unit", ERROR)
            avg_temp, avg_filtered = await avg_and_filtered_temp(
                sources=sources, results=results
            )
            day_or_night_emoji = (
                locale.emoji_weather_now_day()
                if aggregated.get("is_day")
                else locale.emoji_weather_now_night()
            )
            time = aggregated.get("time", ERROR)

            header = locale.message_weather_now_header(
                city=city,  # Из бд пользователя
                time=time,
                day_or_night_emoji=day_or_night_emoji,
                avg_temp=avg_temp,
                temp_unit=temp_unit,
                avg_filtered=avg_filtered,
            )
            sources_text = await connect_templates(
                locale=locale,
                results=results,
                sources=sources,
                temp_unit=temp_unit,
            )

            weather_now_msg = header + "\n" + sources_text.strip()

            # Удаление старого кеша перед сохранением нового
            current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
            prev_hour = current_hour - timedelta(hours=1)
            prev_ymdhm = prev_hour.strftime("%Y%m%d%H")
            prev_weather_id = f"{city}{prev_ymdhm}"

            if await weather_repo.exists(prev_weather_id):
                await weather_repo.delete(prev_weather_id)
                _lg.debug(f"Deleted old weather cache: {prev_weather_id}")

            # New Redis cache
            await weather_repo.save_from_weather_id(
                weather_id=weather_id,
                weather_now_msg=weather_now_msg,
            )

            return weather_now_msg

    except Exception as e:
        _lg.error(f"Internal error: {e}")


@staticmethod
async def get_weather_hours(
    locale: TranslatorRunner,
    weather_repo,
    hours: int,
    city: str | None = None,
    latitude: str | float | None = None,
    longitude: str | float | None = None,
    usr_loc: dict[str, str] | None = None,
) -> BytesIO | None:
    """Get hourly weather forecast"""
    try:
        if usr_loc is not None:
            latitude = usr_loc.get("latitude", None)
            longitude = usr_loc.get("longitude", None)

        if city is not None and latitude is None and longitude is None:
            cord = await get_cord_from_city(name_city=city)

            latitude = cord.get("lat", None)
            longitude = cord.get("lon", None)

        if city is None and latitude and longitude:
            city = await get_city_from_cord(latitude=latitude, longitude=longitude)

        if latitude is None or longitude is None:
            _lg.error(f"Latitude: {latitude}, and Longitude: {longitude}. Error!")
            return None

        ymdhm = datetime.now().strftime("%Y%m%d%H")
        weather_id = f"hours_{city}{ymdhm}_{hours}"

        # Redis cache
        if await weather_repo.exists(weather_id):
            cached_data = await weather_repo.get_by_id(weather_id)
            _lg.debug(f"Returning cached hourly forecast for {city}")
            # Возвращаем байты как BytesIO
            return BytesIO(cached_data["weather_hours_msg"])
        else:
            # Собрать все данные
            results = {}
            # ! Расположены в порядке сортировки
            # YandexParser
            results["YandexParser"] = await yan_get_weather_hours(
                locale=locale,
                latitude=latitude,
                longitude=longitude,
            )

            # OpenMeteo
            results["OpenMeteo"] = await opm_get_weather_hours(
                locale=locale,
                latitude=latitude,
                longitude=longitude,
            )

            # Google
            results["Google"] = await goo_get_weather_hours(
                locale=locale,
                latitude=latitude,
                longitude=longitude,
            )

            # WeatherAPI
            results["WeatherAPI"] = await wapi_get_weather_hours(
                locale=locale,
                latitude=latitude,
                longitude=longitude,
            )

            # VisualCrossing
            results["VisualCrossing"] = await vsc_get_weather_hours(
                locale=locale,
                latitude=latitude,
                longitude=longitude,
            )

            _lg.debug(f"Results is - {results}")

            # Генерировать и отправить изображение
            image_data = await generate_hourly_forecast_image(
                results, hours_count=hours
            )

            # Сохранение в кеш (используем .getvalue() для получения bytes)
            if image_data:
                # Удаление старого кеша (как в weather_now)
                current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
                prev_hour = current_hour - timedelta(hours=1)
                prev_ymdhm = prev_hour.strftime("%Y%m%d%H")
                prev_weather_id = f"hours_{city}{prev_ymdhm}_{hours}"

                if await weather_repo.exists(prev_weather_id):
                    await weather_repo.delete(prev_weather_id)
                    _lg.debug(f"Deleted old hourly cache: {prev_weather_id}")

                # Сохраняем байты картинки
                await weather_repo.save_from_weather_id(
                    weather_id=weather_id,
                    weather_hours_msg=image_data.getvalue(),
                )

                # Возвращаем указатель в начало буфера после getvalue() для корректной отправки
                image_data.seek(0)

            return image_data

    except Exception as e:
        _lg.error(f"Internal error: {e}")


@staticmethod
async def get_weather_5d() -> None:
    """Get 5-day weather forecast - NOT IMPLEMENTED"""
    try:
        pass
    except Exception as e:
        _lg.error(f"Internal error: {e}")


@staticmethod
async def get_weather_astro(
    locale: TranslatorRunner,
    weather_repo,
    city: str | None = None,
    latitude: str | float | None = None,
    longitude: str | float | None = None,
    usr_loc: dict[str, str] | None = None,
) -> str | None:
    """Get day/night weather"""
    try:
        if usr_loc is not None:
            latitude = usr_loc.get("latitude", None)
            longitude = usr_loc.get("longitude", None)

        if city is not None and latitude is None and longitude is None:
            cord = await get_cord_from_city(name_city=city)

            latitude = cord.get("lat", None)
            longitude = cord.get("lon", None)

        if city is None and latitude and longitude:
            city = await get_city_from_cord(latitude=latitude, longitude=longitude)

        if latitude is None or longitude is None:
            _lg.error(f"Latitude: {latitude}, and Longitude: {longitude}. Error!")
            return None

        ymdhm = datetime.now().strftime("%Y%m%d%H")
        weather_id = f"astro_{city}{ymdhm}"

        # Redis cache
        if await weather_repo.exists(weather_id):
            weather_now_msg = await weather_repo.get_by_id(weather_id)
            return weather_now_msg["weather_astro_msg"]

        else:
            results = {}
            # ! Расположены в порядке сортировки
            # 1. Получаем специфичные данные астрономии
            results["WeatherAPI"] = await wapi_get_weather_astro(
                locale=locale, latitude=latitude, longitude=longitude, city=city
            )

            _lg.debug(f"Astro Results is - {results}")

            astro = results.get("WeatherAPI")
            if not astro:
                return locale.message_service_error_not_found_in_service()

            weather_now_data = await wapi_get_weather_now(
                locale=locale, latitude=latitude, longitude=longitude
            )

            moon_phases = {
                "New Moon": "Новолуние",
                "Waxing Crescent": "Растущий серп",
                "First Quarter": "Первая четверть",
                "Waxing Gibbous": "Растущая луна",
                "Full Moon": "Полнолуние",
                "Waning Gibbous": "Убывающая луна",
                "Last Quarter": "Последняя четверть",
                "Waning Crescent": "Убывающий серп",
            }

            phase_rus = moon_phases.get(astro["moon_phase"], astro["moon_phase"])
            header_emoji = (
                locale.emoji_weather_now_day()
                if astro["is_sun_up"]
                else locale.emoji_weather_now_night()
            )

            weather_astro_msg = (
                f"{header_emoji} Астрономия: {city}\n"
                f"День:\n"
                f"  ☀️ Восход: {astro['sunrise']}\n"
                f"  🌇 Закат: {astro['sunset']}\n"
                f"  ⏱ Долгота: {astro['day_length']}\n"
                f"Ночь:\n"
                f"  🌙 Фаза: {phase_rus} ({astro['moon_illumination']}%)\n"
                f"  🌌 Восход луны: {astro['moonrise']}\n"
                f"  🌌 Закат луны: {astro['moonset']}\n"
                f"  🌡 Температура сейчас: {weather_now_data.get('temp')}°C"
            )

            # Redis cache
            await weather_repo.save_from_weather_id(
                weather_id=weather_id,
                weather_astro_msg=weather_astro_msg,
            )

            return weather_astro_msg

    except Exception as e:
        _lg.error(f"Internal error: {e}")


@staticmethod
async def get_weather_rain() -> None:
    """Get precipitation data - NOT IMPLEMENTED"""
    try:
        pass
    except Exception as e:
        _lg.error(f"Internal error: {e}")


@staticmethod
async def get_weather_wind_pressure() -> None:
    """Get wind and pressure data - NOT IMPLEMENTED"""
    try:
        pass
    except Exception as e:
        _lg.error(f"Internal error: {e}")


if __name__ == "__main__":

    async def main():
        from common.core import setup_logging

        setup_logging(level="DEBUG")

    asyncio.run(main())
