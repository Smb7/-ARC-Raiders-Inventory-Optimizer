from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_db
from app.schemas.auth import ConnectRequest, ConnectResponse
from app.services.arc_tracker import ArcTrackerAuthError, ArcTrackerClient, ArcTrackerError
from app.api.deps import get_arc_client

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/connect", response_model=ConnectResponse)
async def connect(
    payload: ConnectRequest,
    db: AsyncSession = Depends(get_db),
    client: ArcTrackerClient = Depends(get_arc_client),
) -> ConnectResponse:
    try:
        await client.fetch_stash(payload.token)
    except ArcTrackerAuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ARC Tracker token") from exc
    except ArcTrackerError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="ARC Tracker unavailable") from exc

    user = User(arc_tracker_token=payload.token, remember_token=payload.remember_me)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return ConnectResponse(user_id=user.id, remember_me=user.remember_token)
