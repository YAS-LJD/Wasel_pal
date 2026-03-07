from fastapi import APIRouter

router = APIRouter(prefix="/predict", tags=["Predict"])


@router.post("")
def predict_risk():
    return {"risk_level": "medium"}
