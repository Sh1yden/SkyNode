from typing import Any, Dict

from aiogram import Router
from aiogram.types import CallbackQuery, Message, User

from fluentogram import TranslatorRunner

from common.core import get_logger
from bot.src.filters import AdminCallback, IsAdmin

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
        if callback_data.action == "admin_menu":
            await message.answer(
                text=locale.message_admin_main_menu(
                    admin_name=user.first_name,
                    user_count=await repos["user_repo"].count_users(),
                ),
            )
    except Exception as e:
        _lg.error(f"Error in callback handler: {e}")
        await callback.answer(locale.message_service_error(error=e), show_alert=True)
