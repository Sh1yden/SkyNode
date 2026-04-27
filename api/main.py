from fastapi import FastAPI
from api.endpoints import router as main_router
from api.lifespan import lifespan


app = FastAPI(
    title="SkyNode",
    version="v0.5.0",
    docs_url="/api/swagger_docs",
    redoc_url="/api/redoc_docs",
    openapi_url="/api/openapi",
    lifespan=lifespan,
)

app.include_router(main_router, prefix="/api", tags=["api"])
