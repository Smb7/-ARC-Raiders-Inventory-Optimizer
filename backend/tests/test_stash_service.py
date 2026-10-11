import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ItemStatic
from app.db.seed import seed_static_data
from app.services.arc_tracker import ArcTrackerClient
from app.services.stash import StashService


@pytest.mark.asyncio
async def test_scan_token_normalizes_seed_items(db: Session) -> None:
    seed_static_data(db)
    items = list(db.scalars(select(ItemStatic)).all())

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"items": [{"id": "metal_parts", "quantity": 40}, {"id": "unknown_item", "quantity": 1}]},
        )

    client = ArcTrackerClient(
        base_url="https://arctracker.io",
        transport=httpx.MockTransport(handler),
    )
    result = await StashService(client).scan_token("token", items)
    await client.aclose()

    assert result.total_quantity == 41
    assert result.unknown_count == 1
    assert result.items[0].name == "Metal Parts"
