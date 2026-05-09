from common.core import get_logger

_lg = get_logger()


async def bot_cleanup(
    runner,
    bot,
    storage,
    repos,
    tuna_process,
):
    _lg.info("Starting cleanup:")

    # Cleanup
    # Stop web server
    if runner:  # type: ignore
        try:
            await runner.cleanup()
            _lg.info("Web server stopped.")
        except Exception as e:
            _lg.error(f"Error stopping web server: {e}.")

    # Delete webhook and close bot
    if bot:  # type: ignore
        try:
            await bot.delete_webhook(drop_pending_updates=False)
            _lg.info("Webhook deleted.")
        except Exception as e:
            _lg.error(f"Error deleting webhook: {e}.")

        try:
            await bot.session.close()
            _lg.info("Bot session closed.")
        except Exception as e:
            _lg.error(f"Error closing bot: {e}.")

    # Close storage
    try:
        await storage.close()
        _lg.info("Storage closed.")
    except Exception as e:
        _lg.error(f"Error closing storage: {e}.")

    # Close database
    if repos:  # type: ignore
        try:
            # Redis
            if repos["user_repo"].db_methods.cache:
                await repos["user_repo"].db_methods.cache.close()
                _lg.info("Redis cache closed.")

            # DB
            await repos["user_repo"].db_methods.close()
            _lg.info("Database closed.")
        except Exception as e:
            _lg.error(f"Error closing database: {e}.")

    # Stop Tuna tunnel
    if tuna_process:
        try:
            _lg.debug("Stopping Tuna tunnel...")
            tuna_process.terminate()
            tuna_process.wait(timeout=3)
            _lg.info("Tuna tunnel stopped.")
        except Exception:
            try:
                tuna_process.kill()
                _lg.warning("Tuna tunnel killed.")
            except Exception as e:
                _lg.error(f"Error killing Tuna: {e}.")

    _lg.info("Cleanup completed!")


async def api_cleanup(repos):
    # Close database
    if repos:  # type: ignore
        try:
            # Redis
            if repos["user_repo"].db_methods.cache:
                await repos["user_repo"].db_methods.cache.close()
                _lg.info("Redis cache closed.")

            # DB
            await repos["user_repo"].db_methods.close()
            _lg.info("Database closed.")
        except Exception as e:
            _lg.error(f"Error closing database: {e}.")
