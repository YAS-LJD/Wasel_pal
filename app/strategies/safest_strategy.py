from app.strategies.base_strategy import RouteStrategy


class SafestStrategy(RouteStrategy):
    def compute(self, payload: dict):
        return {"strategy": "safest", "path": [], "eta_minutes": 15, "risk_score": 0.2}
