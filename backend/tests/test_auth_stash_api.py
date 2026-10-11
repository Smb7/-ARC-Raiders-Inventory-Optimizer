from collections.abc import AsyncGenerator
from uuid import UUID

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import get_arc_client
from app.db.base import Base
from app.db.seed import SAMPLE_ITEMS
from app.db.models import ItemStatic
from app.db.session import get_db
from app.main import app
from app.services.arc_tracker import ArcTrackerClient


@pytest.fixture()
def api_client() -> TestClient:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def prepare() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with session_factory() as session:
            session.add_all([ItemStatic(**item) for item in SAMPLE_ITEMS])
            await session.commit()

    import asyncio

    asyncio.run(prepare())

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    def override_arc_client() -> ArcTrackerClient:
        def handler(request: httpx.Request) -> httpx.Response:
            auth = request.headers.get("Authorization", "")
            if auth != "Bearer valid-token":
                return httpx.Response(401, json={"error": "unauthorized"})
            return httpx.Response(200, json={"items": [{"id": "metal_parts", "quantity": 8}]})

        return ArcTrackerClient(
            base_url="https://arctracker.io",
            transport=httpx.MockTransport(handler),
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_arc_client] = override_arc_client
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_connect_rejects_invalid_token(api_client: TestClient) -> None:
    response = api_client.post("/api/v1/auth/connect", json={"token": "nope", "remember_me": False})
    assert response.status_code == 401


def test_connect_and_scan_stash(api_client: TestClient) -> None:
    connect = api_client.post("/api/v1/auth/connect", json={"token": "valid-token", "remember_me": True})
    assert connect.status_code == 200
    user_id = UUID(connect.json()["user_id"])

    stash = api_client.get(f"/api/v1/stash/{user_id}")
    assert stash.status_code == 200
    body = stash.json()
    assert body["total_quantity"] == 8
    assert body["items"][0]["name"] == "Metal Parts"
    assert body["items"][0]["known"] is True
