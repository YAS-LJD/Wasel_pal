from fastapi import APIRouter

router = APIRouter(prefix="/external", tags=["External"])


@router.get("/health")
def external_health():
    return {"status": "ok"}
