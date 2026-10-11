import httpx
import pytest

from app.services.arc_tracker import ArcTrackerAuthError, ArcTrackerClient, ArcTrackerError


def _transport(status_code: int, payload: object | None = None) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v2/user/stash"
        assert request.headers["Authorization"] == "Bearer test-token"
        return httpx.Response(status_code, json=payload or {"items": []})

    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_fetch_stash_success() -> None:
    client = ArcTrackerClient(base_url="https://arctracker.io", transport=_transport(200, {"items": [{"id": "x"}]}))
    payload = await client.fetch_stash("test-token")
    assert payload == {"items": [{"id": "x"}]}
    await client.aclose()


@pytest.mark.asyncio
async def test_fetch_stash_invalid_token() -> None:
    client = ArcTrackerClient(base_url="https://arctracker.io", transport=_transport(401))
    with pytest.raises(ArcTrackerAuthError):
        await client.fetch_stash("test-token")
    await client.aclose()


@pytest.mark.asyncio
async def test_fetch_stash_unavailable() -> None:
    client = ArcTrackerClient(base_url="https://arctracker.io", transport=_transport(503))
    with pytest.raises(ArcTrackerError):
        await client.fetch_stash("test-token")
    await client.aclose()


@pytest.mark.asyncio
async def test_fetch_stash_sends_app_key() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-App-Key"] == "app-secret"
        assert request.headers["Authorization"] == "Bearer test-token"
        return httpx.Response(200, json={"items": []})

    client = ArcTrackerClient(
        base_url="https://arctracker.io",
        app_key="app-secret",
        transport=httpx.MockTransport(handler),
    )
    payload = await client.fetch_stash("test-token")
    assert payload == {"items": []}
    await client.aclose()


@pytest.mark.asyncio
async def test_fetch_stash_missing_app_key() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={"error": {"code": "missing_app_key", "message": "App key required"}},
        )

    client = ArcTrackerClient(base_url="https://arctracker.io", transport=httpx.MockTransport(handler))
    with pytest.raises(ArcTrackerError, match="app key"):
        await client.fetch_stash("test-token")
    await client.aclose()
