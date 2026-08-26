from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault
from fluentogram import TranslatorHub

from common.core import get_logger

_lg = get_logger()


async def setup_bot_command_pannel(
    bot: Bot,
    dp: Dispatcher,
    admin_ids: list[int],
) -> None:
    try:
        # ! Добавление команд без заглавных букв и в хендлерах тоже исправлять если хотите сюда добавить. В общем строго snake_case!!!

        t_hub = dp.workflow_data.get("t_hub")
        locale = t_hub.get_translator_by_locale(t_hub.root_locale)

        user_commands = [
            BotCommand(
                command="start", description=locale.message_command_panel_start()
            ),
            BotCommand(command="help", description=locale.message_command_panel_help()),
            BotCommand(
                command="showset_location",
                description=locale.message_command_panel_weather_showset_location(),
            ),
            BotCommand(
                command="change_location",
                description=locale.message_command_panel_weather_change_location(),
            ),
            BotCommand(
                command="weather_menu",
                description=locale.message_command_panel_weather_menu(),
            ),
            BotCommand(
                command="weather_now",
                description=locale.message_command_panel_weather_now(),
            ),
        ]

        await bot.set_my_commands(
            commands=user_commands,
            scope=BotCommandScopeDefault(),
        )

        if admin_ids:
            admin_commands = user_commands + [
                BotCommand(
                    command="admin_menu",
                    description=locale.message_command_panel_admin_menu(),
                ),
                BotCommand(
                    command="admin_help",
                    description=locale.message_command_panel_admin_help(),
                ),
            ]

            for admin_id in admin_ids:
                try:
                    await bot.set_my_commands(
                        commands=admin_commands,
                        scope=BotCommandScopeChat(chat_id=admin_id),
                    )
                except Exception as e:
                    _lg.error(f"Admin panel commands set error: {e}")
                    continue

        _lg.debug("Panel bot commands set.")

    except Exception as e:
        _lg.error(f"Internal error: {e}.")
