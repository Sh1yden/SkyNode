from typing import Any, Dict

from aiogram import Bot, Router, html
from aiogram.filters import Command
from aiogram.types import Message, User
from fluentogram import TranslatorRunner

from common.core import get_logger
from bot.src.filters import AdminCallback, IsAdmin
from bot.src.keyboards import (
    get_btns_start,
    get_btns_exit_to_main_menu,
    get_btns_admin_menu,
)

from bot.src.utils import send_photo_save

router = Router()
_lg = get_logger()


# обработка команды /start
@router.message(Command("start"), IsAdmin())
async def command_start_handler(
    message: Message,
    locale: TranslatorRunner,
    repos: Dict[str, Any],
    is_admin: bool,
) -> None:
    """Handle /start command and display welcome message"""
    try:
        user: User | None = message.from_user

        if user is None:
            _lg.warning("User is None in start handler")
            await message.answer(locale.message_service_error_not_user_enable())
            return

        full_name_user = html.bold(message.from_user.full_name)  # type: ignore
        _lg.debug(f"User: {full_name_user}")

        main_menu_text = f"{locale.message_start_hello()}{full_name_user or 'Пользователь'}{locale.message_start_main_menu()}"
        _lg.debug("Main menu text prepared.")

        photo = await send_photo_save("SkyNode Welcome Message")

        await message.answer_photo(
            photo=photo,
            caption=main_menu_text,
            reply_markup=get_btns_start(locale, is_admin),
        )

        # Создание пользователя в БД
        user_repo = repos["user_repo"]
        if not await user_repo.exists(user.id):
            await user_repo.save_from_telegram_user(user)
            _lg.debug(f"New user created: {user.id}")

    except Exception as e:
        _lg.critical(f"Internal error: {e}.")


# обработка команды /admin_help
@router.message(Command("admin_help"), IsAdmin())
async def command_help_handler(message: Message, locale: TranslatorRunner):
    """Handle /admin_help command"""
    try:
        await message.answer(
            text=locale.message_admin_help(),
            reply_markup=get_btns_exit_to_main_menu(locale),
        )

    except Exception as e:
        _lg.critical(f"Internal error: {e}.")


@router.message(Command("admin_menu"), IsAdmin())
async def command_admin_menu_handler(
    message: Message,
    locale: TranslatorRunner,
    repos: Dict[str, Any],
    bot: Bot,
    is_admin: bool,
):
    """Handle /admin_menu command"""
    try:
        user: User | None = message.from_user

        if user is None:
            _lg.warning("User is None")
            await message.answer(locale.message_service_error_not_user_enable())
            return

        full_name_user = user.full_name
        admin_name = f"{full_name_user or 'Пользователь'}"
        user_count = await repos["user_repo"].count_users()

        check_db_status = await repos["admin_repo"].check_status_db()
        if check_db_status:
            db_status = locale.message_admin_db_status_true()
        else:
            db_status = locale.message_admin_db_status_false()

        check_redis_status = await repos["admin_repo"].check_status_redis()
        if check_redis_status:
            redis_status = locale.message_admin_redis_status_true()
        else:
            redis_status = locale.message_admin_redis_status_false()

        tunnel_status = locale.message_admin_tunnel_status_true()

        await message.answer(
            text=locale.message_admin_main_menu(
                admin_name=admin_name,
                user_count=user_count,
                db_status=db_status,
                redis_status=redis_status,
                tunnel_status=tunnel_status,
            ),
            reply_markup=get_btns_admin_menu(locale),
        )

    except Exception as e:
        _lg.critical(f"Internal error: {e}.")


@router.message(Command("get_file_id"), IsAdmin())
async def command_get_file_id_handler(
    message: Message,
    locale: TranslatorRunner,
) -> None:
    """Handle /get_file_id command"""
    try:
        if message.photo:
            await message.answer(
                locale.message_admin_get_file_id(file_id=message.photo[-1].file_id)
            )

    except Exception as e:
        _lg.critical(f"Internal error: {e}.")
