from typing import Any, Dict

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    FSInputFile,
    InputMediaPhoto,
    Location,
    Message,
    ReplyKeyboardRemove,
    User,
)
from fluentogram import TranslatorRunner

from bot.src.core import get_logger
from bot.src.filters import DeviceCallback, WeatherCallback
from bot.src.keyboards import (
    get_btns_device,
    get_btns_location,
    get_btns_start,
    get_btns_weather_menu,
    get_btns_exit_to_weather_menu,
    get_btns_weather_hours,
    get_btns_exit_to_hours_menu,
    get_btns_settings,
)

# cord
from bot.src.services import get_city_from_cord, get_cord_from_city

# weather
from bot.src.services import get_weather_now, get_weather_hours
from bot.src.services import get_weather_astro

from bot.src.states import LocationState
from bot.src.utils import clear_state

router = Router()
_lg = get_logger()


# WEATHER MENU
@router.callback_query(WeatherCallback.filter())
async def weather_callback_handler(
    callback: CallbackQuery,
    callback_data: WeatherCallback,
    locale: TranslatorRunner,
    repos: Dict[str, Any],
) -> None:
    """Handle weather menu callbacks"""

    _lg.debug("CALLBACK HANDLER CALLED!")
    _lg.debug(f"Action: {callback_data.action}")
    _lg.debug(f"User: {callback.from_user.id}")
    _lg.debug(f"Message exists: {callback.message is not None}")
    _lg.debug(f"CALLBACK HANDLER TRIGGERED: {callback_data.action}")

    # Проверяем, что сообщение доступно для редактирования
    if not isinstance(callback.message, Message):
        _lg.warning("Cannot edit inaccessible message.")
        await callback.answer(locale.message_service_error_not_edit())
        return

    message: Message | None = callback.message
    user: User | None = callback.from_user
    user_repo = repos["user_repo"]
    weather_repo = repos["weather_repo"]

    try:
        # 📚 Вызов всего меню
        if callback_data.action == "weather_menu":
            if message.text:
                await message.edit_text(
                    text=locale.message_weather_menu(),
                    reply_markup=await get_btns_weather_menu(
                        user_id=user.id, locale=locale, user_repo=user_repo
                    ),
                )
            elif message.photo:
                await message.delete()
                await message.answer(
                    text=locale.message_weather_menu(),
                    reply_markup=await get_btns_weather_menu(
                        user_id=user.id, locale=locale, user_repo=user_repo
                    ),
                )

        # 🌡 Сейчас
        if callback_data.action == "weather_now":
            if await user_repo.has_location(user.id):
                location = await user_repo.get_by_id(user.id)
                latitude = location.get("latitude", None)
                longitude = location.get("longitude", None)
                city = location.get("city")

                all_msg = await get_weather_now(
                    locale=locale,
                    weather_repo=weather_repo,
                    city=city,
                    latitude=latitude,
                    longitude=longitude,
                    usr_loc=location,
                )

                _lg.debug(f"all_msg is - {all_msg}")

                await message.edit_text(
                    text=str(all_msg),
                    reply_markup=get_btns_exit_to_weather_menu(locale),
                )
            else:
                await message.edit_text(
                    text=locale.message_location_not_posted(),
                    reply_markup=get_btns_exit_to_weather_menu(locale),
                )

        # 📊 Почасовое меню
        elif callback_data.action == "weather_hours":
            if await user_repo.has_location(user.id):
                location = await user_repo.get_by_id(user.id)
                latitude = location.get("latitude", None)
                longitude = location.get("longitude", None)
                city = location.get("city")

                if message.text:
                    await message.edit_text(
                        text=locale.message_weather_hours_menu(),
                        reply_markup=get_btns_weather_hours(locale),
                    )
                elif message.photo:
                    await message.delete()
                    await message.answer(
                        text=locale.message_weather_hours_menu(),
                        reply_markup=get_btns_weather_hours(locale),
                    )
            else:
                await message.edit_text(
                    text=locale.message_location_not_posted(),
                    reply_markup=get_btns_exit_to_weather_menu(locale),
                )
        # По периоду времени
        elif callback_data.action.startswith("weather_hours_"):
            if await user_repo.has_location(user.id):
                location = await user_repo.get_by_id(user.id)
                latitude = location.get("latitude", None)
                longitude = location.get("longitude", None)
                city = location.get("city")

                hours_count = int(callback_data.action.split("_")[-1])

                image_buffer = await get_weather_hours(
                    hours=hours_count,
                    locale=locale,
                    weather_repo=weather_repo,
                    city=city,
                    longitude=longitude,
                    latitude=latitude,
                )

                photo_file = BufferedInputFile(
                    image_buffer.getvalue(), filename="forecast_{hours_count}h.png"
                )

                caption = locale.message_weather_hours_pattern(hours_count=hours_count)

                await message.edit_media(
                    media=InputMediaPhoto(media=photo_file, caption=caption),
                    reply_markup=get_btns_exit_to_hours_menu(locale),
                )
            else:
                await message.edit_text(
                    text=locale.message_location_not_posted(),
                    reply_markup=get_btns_exit_to_weather_menu(locale),
                )

        # 🔅 День / Ночь
        elif callback_data.action == "weather_day_night":
            if await user_repo.has_location(user.id):
                location = await user_repo.get_by_id(user.id)
                latitude = location.get("latitude", None)
                longitude = location.get("longitude", None)
                city = location.get("city")

                astro_text = await get_weather_astro(
                    locale=locale,
                    weather_repo=weather_repo,
                    city=city,
                    latitude=latitude,
                    longitude=longitude,
                )

                await message.edit_text(
                    text=astro_text,
                    reply_markup=get_btns_exit_to_weather_menu(locale),
                )
            else:
                await message.edit_text(
                    text=locale.message_location_not_posted(),
                    reply_markup=get_btns_exit_to_weather_menu(locale),
                )

        # 📆 На 5 дней
        elif callback_data.action == "weather_5d":
            await message.edit_text(
                text=locale.message_service_in_development(),
                reply_markup=get_btns_exit_to_weather_menu(locale),
            )

        # 🌦 Осадки
        elif callback_data.action == "weather_rain":
            await message.edit_text(
                text=locale.message_service_in_development(),
                reply_markup=get_btns_exit_to_weather_menu(locale),
            )

        # 🧭 Ветер/давление
        elif callback_data.action == "weather_wind_pressure":
            await message.edit_text(
                text=locale.message_service_in_development(),
                reply_markup=get_btns_exit_to_weather_menu(locale),
            )

        # 📍 Локация
        elif callback_data.action == "weather_location":
            if await user_repo.has_location(user.id):
                location = await user_repo.get_by_id(user.id)

                city = location.get("city")
                latitude = location.get("latitude")
                longitude = location.get("longitude")

                await message.edit_text(
                    text=locale.message_location_good_send(
                        city=city,
                        latitude=latitude,
                        longitude=longitude,
                    ),
                    reply_markup=get_btns_exit_to_weather_menu(locale),
                )
            else:
                await message.edit_text(
                    text=locale.message_device_select(),
                    reply_markup=get_btns_device(locale),
                )
        elif callback_data.action == "change_weather_location":
            await message.edit_text(
                text=locale.message_device_select(),
                reply_markup=get_btns_device(locale),
            )

        # ⚙️ Настроить
        if callback_data.action == "weather_settings":
            await message.edit_text(
                text=locale.message_settings_menu(),
                reply_markup=get_btns_settings(locale),
            )

        # 🔔 Подписка
        elif callback_data.action == "weather_subscription":
            await message.edit_text(
                text=locale.message_service_in_development(),
                reply_markup=get_btns_exit_to_weather_menu(locale),
            )

        # 🔙 Назад
        elif callback_data.action == "weather_get_back":
            full_name_user = user.full_name
            main_menu_text = (
                f"{locale.message_start_hello()}"
                f"{full_name_user or 'Пользователь'}"
                f"{locale.message_start_main_menu()}"
            )

            photo = FSInputFile("assets/images/messages/SkyNode Welcome Message.png")

            await message.edit_media(
                media=InputMediaPhoto(media=photo, caption=main_menu_text),
                text=main_menu_text,
                reply_markup=get_btns_start(locale),
            )

        # Ответ что callback обработан
        await callback.answer()

    except Exception as e:
        _lg.error(f"Error in callback handler: {e}")
        await callback.answer(locale.message_service_error_not_edit(), show_alert=True)


# DEVICE
@router.callback_query(DeviceCallback.filter())
async def device_callback_handler(
    callback: CallbackQuery,
    callback_data: DeviceCallback,
    locale: TranslatorRunner,
    state: FSMContext,
):
    # Проверяем, что сообщение доступно для редактирования
    if not isinstance(callback.message, Message):
        _lg.warning("Cannot edit inaccessible message.")
        await callback.answer(locale.message_service_error_not_edit())
        return

    message: Message | None = callback.message

    if callback_data.action == "device_phone":
        # Установить состояние ожидания геолокации
        await state.set_state(LocationState.waiting_for_city_phone)

        await message.answer(
            text=locale.message_location_send_on_phone(),
            reply_markup=get_btns_location(locale),
        )

    if callback_data.action == "device_pc":
        # Установить состояние ожидания города
        await state.set_state(LocationState.waiting_for_city_pc)

        # Сообщение ожидания названии локации
        await message.answer(text=locale.message_location_send_on_pc())


# LOCATION
@router.message(LocationState.waiting_for_city_phone, F.location)
async def handle_location_phone(
    message: Message, locale: TranslatorRunner, repos: Dict[str, Any], state: FSMContext
) -> None:
    """Handle location from phone"""
    try:
        _lg.debug("Start handle location on phone.")

        location_phone: Location | None = message.location
        user: User | None = message.from_user

        if user is None:
            _lg.warning("User is None")
            await message.answer(text=locale.message_service_error_not_user_enable())
            await clear_state(state)
            return

        if not location_phone:
            await message.answer(text=locale.message_location_save_error())
            await clear_state(state)
            return

        lat = location_phone.latitude
        lon = location_phone.longitude
        city = await get_city_from_cord(lat, lon)

        if not city:
            _lg.warning(f"Failed to get city name for coordinates: {lat}, {lon}")
            city = "Unknown"

        _lg.debug(f"User city on phone is - {city}.")

        user_repo = repos["user_repo"]
        success = await user_repo.update_location(user.id, city, lat, lon)

        if success:
            _lg.debug(str(success))
            msg_text = locale.message_location_good_send(
                city=city,
                latitude=lat,
                longitude=lon,
            )
            await message.answer(
                text=msg_text,
                reply_markup=get_btns_exit_to_weather_menu(locale),
            )
        else:
            await message.answer(text=locale.message_location_save_error())

        await clear_state(state)

    except Exception as e:
        _lg.error(f"Internal error: {e}.")
        await clear_state(state)


@router.message(LocationState.waiting_for_city_pc, F.text)
async def handle_location_pc(
    message: Message, locale: TranslatorRunner, repos: Dict[str, Any], state: FSMContext
) -> None:
    """Handle location from PC (city name as text)"""
    try:
        _lg.debug("Start handle location on PC.")

        location_pc = message.text
        user: User | None = message.from_user

        if user is None:
            _lg.warning("User is None")
            await message.answer(text=locale.message_service_error_not_user_enable())
            await clear_state(state)
            return

        # Check for cancel command
        cancel_button = locale.button_location_cancel()
        if location_pc == cancel_button or location_pc == "отмена":
            await clear_state(state)
            await message.answer(
                text=locale.message_location_cancel(),
                reply_markup=get_btns_exit_to_weather_menu(locale),
            )
            return

        # Get coordinates from city name
        cord = await get_cord_from_city(location_pc)

        if not cord or "lat" not in cord or "lon" not in cord:
            _lg.warning(f"Failed to get coordinates for city: {location_pc}")
            await message.answer(
                "❌ Не удалось найти указанный город. "
                "Попробуйте другое название."  # ! заглушка
            )
            return

        lat = cord["lat"]
        lon = cord["lon"]

        # Verify city name via reverse geocoding
        city = await get_city_from_cord(lat, lon)

        if not city:
            _lg.warning(f"Failed to verify city name for coordinates: {lat}, {lon}")
            city = location_pc  # Use user input as fallback

        _lg.debug(f"User city on PC is - {city}.")

        user_repo = repos["user_repo"]
        success = await user_repo.update_location(user.id, city, lat, lon)

        if success:
            _lg.debug(str(success))
            msg_text = locale.message_location_good_send(
                city=city,
                latitude=lat,
                longitude=lon,
            )
            await message.answer(
                text=msg_text,
                reply_markup=get_btns_exit_to_weather_menu(locale),
            )
        else:
            await message.answer(
                text=locale.message_location_save_error(),
                show_alert=True,
                reply_markup=get_btns_exit_to_weather_menu(locale),
            )

        await clear_state(state)

    except Exception as e:
        _lg.error(f"Internal error: {e}.")
        await clear_state(state)


@router.message(
    LocationState.waiting_for_city_phone,
    F.text == "❌ Отмена",  # ! Заглушки
)
@router.message(
    LocationState.waiting_for_city_pc,
    F.text == "❌ Отмена",
)
async def handle_cancel_location(
    message: Message, locale: TranslatorRunner, state: FSMContext
) -> None:
    """Handle location request cancellation"""
    await clear_state(state)
    await message.answer(
        locale.message_location_cancel(),
        reply_markup=ReplyKeyboardRemove(),
    )
