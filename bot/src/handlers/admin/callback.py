from typing import Any, Dict

from aiogram import Router
from aiogram.types import CallbackQuery, Message, User

from fluentogram import TranslatorRunner

from common.core import get_logger
from bot.src.filters import AdminCallback, IsAdmin
from bot.src.keyboards import get_btns_admin_menu

router = Router()
_lg = get_logger()


@router.callback_query(AdminCallback.filter(), IsAdmin())
async def admin_callback_handler(
    callback: CallbackQuery,
    callback_data: AdminCallback,
    locale: TranslatorRunner,
    repos: Dict[str, Any],
    is_admin: bool,
) -> None:
    """Handle admin callbacks"""

    _lg.debug(
        "Callback triggered | action: %s | user: %s | has_msg: %s",
        callback_data.action,
        callback.from_user.id,
        callback.message is not None,
    )

    # Проверяем, что сообщение доступно для редактирования
    if not isinstance(callback.message, Message):
        _lg.warning("Cannot edit inaccessible message.")
        await callback.answer(locale.message_service_error_not_edit())
        return

    message: Message | None = callback.message
    user: User | None = callback.from_user

    try:
        # 🔐 Админ панель
        if callback_data.action == "admin_menu":
            if message.text:
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

                await message.edit_text(
                    text=locale.message_admin_main_menu(
                        admin_name=admin_name,
                        user_count=user_count,
                        db_status=db_status,
                        redis_status=redis_status,
                        tunnel_status=tunnel_status,
                    ),
                    reply_markup=get_btns_admin_menu(locale),
                )
            elif message.photo:
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

                await message.delete()
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
        _lg.error(f"Error in callback handler: {e}")
        await callback.answer(locale.message_service_error(error=e), show_alert=True)
