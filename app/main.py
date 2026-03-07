from fastapi import FastAPI

from app.config import settings
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


app = FastAPI(title=settings.APP_NAME, debug=settings.APP_DEBUG)

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
def health_check():
    return {"message": "Wasel Palestine API is running"}
