from fastapi import APIRouter

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("")
def get_stats():
    return {"incidents": 0, "checkpoints": 0, "alerts": 0}
