from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.routers import (
    alerts,
    auth,
    checkpoints,
    external,
    incidents,
    predict,
    reports,
    routes,
    stats,
    users,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        print("Database connected successfully")
    yield
    await engine.dispose()
    print("Database disconnected")


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.APP_DEBUG,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(users.router, prefix=settings.API_PREFIX)
app.include_router(checkpoints.router, prefix=settings.API_PREFIX)
app.include_router(incidents.router, prefix=settings.API_PREFIX)
app.include_router(reports.router, prefix=settings.API_PREFIX)
app.include_router(routes.router, prefix=settings.API_PREFIX)
app.include_router(alerts.router, prefix=settings.API_PREFIX)
app.include_router(stats.router, prefix=settings.API_PREFIX)
app.include_router(external.router, prefix=settings.API_PREFIX)
app.include_router(predict.router, prefix=settings.API_PREFIX)


@app.get("/")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
