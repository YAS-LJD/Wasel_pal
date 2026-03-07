from fastapi import APIRouter

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("")
def list_incidents():
    return []
