from fastapi import APIRouter

router = APIRouter(prefix="/checkpoints", tags=["Checkpoints"])


@router.get("")
def list_checkpoints():
    return []
