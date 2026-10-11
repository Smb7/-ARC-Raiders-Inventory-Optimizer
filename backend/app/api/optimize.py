from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_stash_service
from app.db.models import ItemStatic, Recipe, RecyclingYield, StackLimit, User
from app.db.session import get_db
from app.schemas.optimize import OptimizeRequest, OptimizeResult, PreferenceUpdate
from app.services.arc_tracker import ArcTrackerAuthError, ArcTrackerError
from app.services.optimizer import optimize_stash
from app.services.stash import StashService, UserNotFoundError

router = APIRouter(prefix="/api/v1", tags=["optimize"])


@router.patch("/users/{user_id}/preferences")
async def update_preferences(
    user_id: UUID,
    payload: PreferenceUpdate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User session not found")

    data = payload.model_dump(exclude_unset=True)
    stack_limits = data.pop("stack_limits", None)
    for field, value in data.items():
        setattr(user, field, value)

    if stack_limits is not None:
        existing = list((await db.scalars(select(StackLimit).where(StackLimit.user_id == user_id))).all())
        for row in existing:
            await db.delete(row)
        for limit in stack_limits:
            db.add(StackLimit(user_id=user_id, item_id=limit["item_id"], max_stacks=limit["max_stacks"]))

    await db.commit()
    return {"status": "ok"}


@router.post("/optimize-stash", response_model=OptimizeResult)
async def optimize_user_stash(
    payload: OptimizeRequest,
    db: AsyncSession = Depends(get_db),
    service: StashService = Depends(get_stash_service),
) -> OptimizeResult:
    try:
        stash = await service.scan_user(db, payload.user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User session not found") from exc
    except ArcTrackerAuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ARC Tracker token") from exc
    except ArcTrackerError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="ARC Tracker unavailable") from exc

    user = await db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User session not found")

    items = list((await db.scalars(select(ItemStatic))).all())
    recipes = list((await db.scalars(select(Recipe).options(selectinload(Recipe.ingredients)))).all())
    yields = list((await db.scalars(select(RecyclingYield))).all())
    limits = {
        row.item_id: row.max_stacks
        for row in (await db.scalars(select(StackLimit).where(StackLimit.user_id == payload.user_id))).all()
    }
    return optimize_stash(
        items=stash.items,
        user=user,
        recipes=recipes,
        yields=yields,
        stack_limits=limits,
        items_by_id={item.id: item for item in items},
    )
