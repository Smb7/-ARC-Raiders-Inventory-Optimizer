from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ItemStatic, User
from app.schemas.stash import NormalizedStash
from app.services.arc_tracker import ArcTrackerClient
from app.services.normalize import normalize_stash


class UserNotFoundError(Exception):
    pass


class StashService:
    def __init__(self, client: ArcTrackerClient) -> None:
        self._client = client

    async def scan_token(self, token: str, items: list[ItemStatic]) -> NormalizedStash:
        payload = await self._client.fetch_stash(token)
        return normalize_stash(payload, {item.id: item for item in items})

    async def scan_user(self, db: AsyncSession, user_id: UUID) -> NormalizedStash:
        user = await db.get(User, user_id)
        if user is None or not user.arc_tracker_token:
            raise UserNotFoundError
        items = list((await db.scalars(select(ItemStatic))).all())
        return await self.scan_token(user.arc_tracker_token, items)
