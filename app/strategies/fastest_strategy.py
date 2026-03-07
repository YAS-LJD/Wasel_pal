from app.strategies.base_strategy import RouteStrategy


class FastestStrategy(RouteStrategy):
    def compute(self, payload: dict):
        return {"strategy": "fastest", "path": [], "eta_minutes": 10, "risk_score": 0.7}
