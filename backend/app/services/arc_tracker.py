from typing import Any

import httpx


class ArcTrackerError(Exception):
    pass


class ArcTrackerAuthError(ArcTrackerError):
    pass


class ArcTrackerClient:
    def __init__(
        self,
        base_url: str,
        transport: httpx.AsyncBaseTransport | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=15.0,
            transport=transport,
        )

    async def fetch_stash(self, token: str) -> Any:
        try:
            response = await self._client.get(
                "/api/v2/user/stash",
                headers={"Authorization": f"Bearer {token}"},
            )
        except httpx.HTTPError as exc:
            raise ArcTrackerError("ARC Tracker request failed") from exc

        if response.status_code in {401, 403}:
            raise ArcTrackerAuthError("Invalid ARC Tracker token")
        if response.status_code >= 400:
            raise ArcTrackerError("ARC Tracker stash request failed")
        return response.json()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()
