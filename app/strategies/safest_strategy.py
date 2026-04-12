from app.strategies.base_strategy import RouteStrategy


class SafestStrategy(RouteStrategy):
    def compute(self, payload: dict):
        checkpoints = payload.get("checkpoints", [])
        
        # تجنب الحواجز المغلقة والمقيدة
        blocked = [c for c in checkpoints if c.get("status") in ("closed", "restricted")]
        open_cp = [c for c in checkpoints if c.get("status") == "open"]
        
        # كل حاجز مغلق يضيف 5 دقائق للمسار البديل
        extra_minutes = len(blocked) * 5
        
        return {
            "strategy": "safest",
            "path": [],
            "eta_minutes": 15 + extra_minutes,
            "risk_score": round(0.1 + (len(open_cp) * 0.05), 2),
            "avoided_checkpoints": len(blocked),
            "meta": f"Avoiding {len(blocked)} closed/restricted checkpoints"
        }