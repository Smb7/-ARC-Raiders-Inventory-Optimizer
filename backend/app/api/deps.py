from fastapi import Depends

from app.core.config import settings
from app.services.arc_tracker import ArcTrackerClient
from app.services.stash import StashService


def get_arc_client() -> ArcTrackerClient:
    return ArcTrackerClient(base_url=settings.arc_tracker_base_url, app_key=settings.arc_tracker_api_key)


def get_stash_service(client: ArcTrackerClient = Depends(get_arc_client)) -> StashService:
    return StashService(client)
