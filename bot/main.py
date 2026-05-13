import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub
from fluentogram.exceptions import (
    FormatError,
    KeyNotFoundError,
    RootTranslatorNotFoundError,
)
from common.core import get_logger, setup_logging
from common.database.core import init_database
from common.database.repositories import create_repositories
from bot.src.handlers import router as main_router
from bot.src.middlewares import (
    DataBaseMiddleware,
    TranslateMiddleware,
    AdminAccessMiddleware,
)
from bot.src.utils import settings, start_cloudflare, ensure_main_admin
from common.utils import bot_cleanup
from bot.src.web.routes import setup_health_routes

storage = MemoryStorage()

setup_logging(level="DEBUG")
_lg = get_logger(__name__)

# Get Telegram bot Token
TOKEN = settings.TELEGRAM_BOT_TOKEN

# Webserver settings
WEB_SERVER_HOST = settings.WEB_SERVER_HOST
WEB_SERVER_PORT = int(settings.WEB_SERVER_PORT)

# Telegram webhook settings:
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = settings.TELEGRAM_WEBHOOK_SECRET


def create_translator_hub() -> TranslatorHub | None:
    try:
        _lg.debug("Creating a TranslatorHub.")

        t_hub = TranslatorHub(
            {"ru": ("ru",)},
            translators=[
                FluentTranslator(
                    "ru",
                    translator=FluentBundle.from_files(
                        "ru-RU",
                        filenames=[
                            "bot/src/i18n/ru/text.ftl",
                            "bot/src/i18n/ru/button.ftl",
                        ],
                    ),
                )
            ],
            root_locale="ru",
        )

        _lg.info("TranslatorHub created successfully.")
        return t_hub

    except KeyNotFoundError as e:
        _lg.critical(f"Translation key not found: {e.key}")
    except RootTranslatorNotFoundError as e:
        _lg.critical(f"Root locale translator missing: {e.root_locale}")
    except FormatError as e:
        _lg.critical(f"Formatting error for key {e.key}: {e.original_error}")
    except Exception as e:
        _lg.critical(f"Internal error: {e}.")


def create_dispatcher(repos) -> Dispatcher | None:
    """
    Create and configure Dispatcher with routers

    Returns:
        Dispatcher | None: Configured dispatcher or None if error
    """
    try:
        _lg.debug("Create Dispatcher.")

        t_hub = create_translator_hub()
        if not t_hub:
            _lg.critical("Failed to create TranslatorHub")
            return None

        dp = Dispatcher(storage=storage, t_hub=t_hub)

        dp.include_router(main_router)

        dp.message.middleware(TranslateMiddleware())
        dp.message.outer_middleware(DataBaseMiddleware(repos=repos))
        dp.message.outer_middleware(AdminAccessMiddleware())

        dp.callback_query.middleware(TranslateMiddleware())
        dp.callback_query.outer_middleware(DataBaseMiddleware(repos=repos))
        dp.callback_query.outer_middleware(AdminAccessMiddleware())

        _lg.info("Dispatcher created successfully.")
        return dp

    except Exception as e:
        _lg.critical(f"Internal error: {e}.")


async def on_startup_set_webhook(bot: Bot, base_webhook_url: str) -> None:
    """Set webhook on startup"""
    try:
        webhook_url = f"{base_webhook_url}{WEBHOOK_PATH}"
        _lg.debug(f"Setting webhook to: {webhook_url}")

        await bot.delete_webhook(drop_pending_updates=True)
        _lg.debug("Old webhook deleted")

        result = await bot.set_webhook(
            url=webhook_url,
            secret_token=WEBHOOK_SECRET,
            allowed_updates=["message", "callback_query"],
        )

        _lg.debug(f"Webhook set result: {result}")

        webhook_info = await bot.get_webhook_info()
        _lg.info(f"Current webhook: {webhook_info.url}")
        _lg.debug(f"Allowed updates: {webhook_info.allowed_updates}")

    except Exception as e:
        _lg.critical(f"Failed to set webhook: {e}")
        raise


def resolve_webhook_base_url() -> tuple[str, object | None]:
    """Use explicit webhook URL in cluster, Tunnel locally."""
    base_webhook_url = settings.BASE_WEBHOOK_URL.strip()
    if base_webhook_url:
        return base_webhook_url.rstrip("/"), None

    return start_cloudflare(WEB_SERVER_PORT)


def create_bot() -> Bot | None:
    """
    Create and configure Telegram bot

    Returns:
        Bot | None: Configured bot instance or None if error
    """
    try:
        _lg.debug("Creating bot.")

        if not TOKEN:
            _lg.critical("Token is empty or invalid.")
            return None

        bot = Bot(
            token=TOKEN,  # type: ignore
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        _lg.info("Bot created successfully.")
        return bot

    except Exception as e:
        _lg.critical(f"Internal error: {e}.")
        return None


async def on_startup_ready(app: web.Application):
    app["is_ready"] = True
    _lg.debug("Application state set to READY via signal")


async def run_bot() -> None:
    """Async main app function."""
    repos = None
    engine = None
    runner = None
    bot = None
    tunnel_process = None

    try:
        _lg.debug("Start main func.")
        _lg.info(f"PROJECT STATUS is - {settings.PROJECT_STATUS}")
        _lg.info(f"Webhook bind target: {WEB_SERVER_HOST}:{WEB_SERVER_PORT}")

        bot = create_bot()
        if bot is None:
            _lg.critical("Failed to create a bot. Exiting.")
            return

        base_webhook_url, tunnel_process = resolve_webhook_base_url()

        engine, SessionLocal = await init_database()  # type: ignore

        repos = await create_repositories(SessionLocal, engine)  # type: ignore
        _lg.info("All Database initialized.")

        await ensure_main_admin(repos["admin_repo"], settings.MAIN_ADMIN_ID)

        dp = create_dispatcher(repos)
        if dp is None:
            _lg.critical("Failed to create a dispatcher. Exiting.")
            return

        # Setup web application
        app = web.Application()
        app.on_startup.append(on_startup_ready)  # type: ignore
        setup_health_routes(app)

        webhook_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=WEBHOOK_SECRET,
        )
        webhook_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        # Start web server
        runner = web.AppRunner(app)
        if runner is None:
            _lg.critical("Failed to create a runner. Exiting.")
            return
        await runner.setup()

        site = web.TCPSite(runner, WEB_SERVER_HOST, WEB_SERVER_PORT)
        await site.start()

        await on_startup_set_webhook(bot, base_webhook_url)

        _lg.info(f"Web server started on {WEB_SERVER_HOST}:{WEB_SERVER_PORT}")
        _lg.info("Bot is running. Press Ctrl+C to stop.")

        await asyncio.Event().wait()

    except asyncio.CancelledError:
        _lg.info("Bot stopped by signal.")
    except KeyboardInterrupt:
        _lg.info("Bot stopped by user.")
    except Exception as e:
        _lg.critical(f"Critical error: {e}.", exc_info=True)
    finally:
        # All bot cleanup
        await bot_cleanup(
            runner,
            bot,  # type: ignore
            storage,
            repos,
            tunnel_process,
        )


def main() -> None:
    """Main point."""
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        _lg.info("Received Ctrl+C.")
    finally:
        _lg.info("Bot stopped.")
        _lg.info("Logging stopped.")
        logging.shutdown()


if __name__ == "__main__":
    main()
