from app.strategies.base_strategy import RouteStrategy


class BalancedStrategy(RouteStrategy):
    def compute(self, payload: dict):
        return {"strategy": "balanced", "path": [], "eta_minutes": 12, "risk_score": 0.4}
