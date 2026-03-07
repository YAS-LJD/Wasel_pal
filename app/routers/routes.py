from fastapi import APIRouter

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.post("/plan")
def plan_route():
    return {"message": "Route planned"}
