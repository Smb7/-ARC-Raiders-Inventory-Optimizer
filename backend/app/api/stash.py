from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_stash_service
from app.db.session import get_db
from app.schemas.stash import NormalizedStash
from app.services.stash import StashService, UserNotFoundError
from app.services.arc_tracker import ArcTrackerAuthError, ArcTrackerError

router = APIRouter(prefix="/api/v1", tags=["stash"])


@router.get("/stash/{user_id}", response_model=NormalizedStash)
async def get_stash(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: StashService = Depends(get_stash_service),
) -> NormalizedStash:
    try:
        return await service.scan_user(db, user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User session not found") from exc
    except ArcTrackerAuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ARC Tracker token") from exc
    except ArcTrackerError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="ARC Tracker unavailable") from exc
