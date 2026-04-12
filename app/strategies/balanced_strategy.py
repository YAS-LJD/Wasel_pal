from app.strategies.base_strategy import RouteStrategy


class BalancedStrategy(RouteStrategy):
    def compute(self, payload: dict):
        checkpoints = payload.get("checkpoints", [])
        
        open_cp     = [c for c in checkpoints if c.get("status") == "open"]
        delayed_cp  = [c for c in checkpoints if c.get("status") == "delayed"]
        blocked_cp  = [c for c in checkpoints if c.get("status") in ("closed", "restricted")]
        
        extra_minutes = (len(delayed_cp) * 2) + (len(blocked_cp) * 4)
        risk = round(0.3 + (len(blocked_cp) * 0.1) + (len(delayed_cp) * 0.05), 2)
        
        return {
            "strategy": "balanced",
            "path": [],
            "eta_minutes": 12 + extra_minutes,
            "risk_score": min(risk, 1.0),
            "open_checkpoints": len(open_cp),
            "delayed_checkpoints": len(delayed_cp),
            "avoided_checkpoints": len(blocked_cp),
            "meta": f"Balanced route: {len(open_cp)} open, {len(delayed_cp)} delayed, avoiding {len(blocked_cp)} blocked"
        }