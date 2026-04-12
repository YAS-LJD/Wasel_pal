from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.alert import Alert, AlertSubscription
from app.schemas.alert import AlertResponse, SubscriptionCreate, SubscriptionResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=list[AlertResponse])
async def list_alerts(
    region:   str | None = None,
    category: str | None = None,
    page:     int = 1,
    limit:    int = 20,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    """قائمة التنبيهات مع فلترة بالمنطقة والفئة وpagination"""
    query = select(Alert)

    if region:
        query = query.where(Alert.region == region)
    if category:
        query = query.where(Alert.category == category)

    query = query.order_by(Alert.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/subscriptions", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def subscribe(
    body: SubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """اشتراك في تنبيهات منطقة أو فئة معينة"""
    sub = AlertSubscription(
        user_id=current_user["id"],
        region=body.region,
        category=body.category,
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return sub


@router.delete("/subscriptions/{sub_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe(
    sub_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """إلغاء اشتراك"""
    result = await db.execute(
        select(AlertSubscription).where(
            AlertSubscription.id == sub_id,
            AlertSubscription.user_id == current_user["id"],
        )
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    await db.delete(sub)
    await db.commit()