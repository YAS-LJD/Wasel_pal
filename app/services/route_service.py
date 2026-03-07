from app.strategies.balanced_strategy import BalancedStrategy
from app.strategies.fastest_strategy import FastestStrategy
from app.strategies.safest_strategy import SafestStrategy


class RouteService:
    def __init__(self):
        self._strategies = {
            "fastest": FastestStrategy(),
            "safest": SafestStrategy(),
            "balanced": BalancedStrategy(),
        }

    def build_route(self, payload: dict):
        selected = payload.get("strategy", "balanced")
        strategy = self._strategies.get(selected, self._strategies["balanced"])
        return strategy.compute(payload)
