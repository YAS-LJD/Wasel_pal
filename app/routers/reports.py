from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("")
def list_reports():
    return []
