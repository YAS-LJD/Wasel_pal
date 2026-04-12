from app.strategies.base_strategy import RouteStrategy


class FastestStrategy(RouteStrategy):
    def compute(self, payload: dict):
        checkpoints = payload.get("checkpoints", [])
        
        # يمر على كل الحواجز بغض النظر عن حالتها
        delayed = [c for c in checkpoints if c.get("status") == "delayed"]
        
        # كل حاجز فيه تأخير يضيف 3 دقائق
        extra_minutes = len(delayed) * 3
        
        return {
            "strategy": "fastest",
            "path": [],
            "eta_minutes": 10 + extra_minutes,
            "risk_score": round(0.5 + (len(checkpoints) * 0.1), 2),
            "passed_checkpoints": len(checkpoints),
            "meta": f"Passing through all {len(checkpoints)} checkpoints"
        }