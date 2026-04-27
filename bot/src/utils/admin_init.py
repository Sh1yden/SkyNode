from bot.src.core import get_logger

_lg = get_logger()


async def ensure_main_admin(admin_repo, admin_id: int) -> None:
    if not await admin_repo.is_admin(admin_id):
        _lg.info(f"Initializing Main Admin: {admin_id} not found. Adding...")
        await admin_repo.add_admin(admin_id)
        _lg.info(f"Main Admin: {admin_id} added.")
    else:
        _lg.info("Initializing: Admin is already in the database.")
