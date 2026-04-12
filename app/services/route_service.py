from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.strategies.balanced_strategy import BalancedStrategy
from app.strategies.fastest_strategy import FastestStrategy
from app.strategies.safest_strategy import SafestStrategy


class RouteService:
    def __init__(self):
        self._strategies = {
            "fastest":  FastestStrategy(),
            "safest":   SafestStrategy(),
            "balanced": BalancedStrategy(),
        }

    async def build_route(self, db: AsyncSession, payload: dict):
        from app.models.checkpoint import Checkpoint

        # جيب الحواجز من DB
        result = await db.execute(select(Checkpoint))
        checkpoints = result.scalars().all()

        payload["checkpoints"] = [
            {
                "id": c.id,
                "name": c.name,
                "status": c.status.value if hasattr(c.status, "value") else str(c.status),
                "latitude": c.latitude,
                "longitude": c.longitude,
            }
            for c in checkpoints
        ]

        selected = payload.get("strategy", "balanced")
        if selected not in self._strategies:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid strategy '{selected}'. Choose from: {list(self._strategies.keys())}"
            )
        return self._strategies[selected].compute(payload)