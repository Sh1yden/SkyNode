from aiohttp import web


async def live_handler(request: web.Request) -> web.Response:
    return web.json_response({"status": "live"})


async def ready_handler(request: web.Request) -> web.Response:
    if request.app.get("is_ready", False):
        return web.json_response({"status": "ready"})

    return web.json_response({"status": "starting"}, status=503)


def setup_health_routes(app: web.Application) -> None:
    app.router.add_get("/live", live_handler)
    app.router.add_get("/ready", ready_handler)
