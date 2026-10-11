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
        app_key: str = "",
        transport: httpx.AsyncBaseTransport | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._app_key = app_key
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=15.0,
            transport=transport,
        )

    def _headers(self, token: str) -> dict[str, str]:
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        if self._app_key:
            headers["X-App-Key"] = self._app_key
        return headers

    async def fetch_stash(self, token: str) -> Any:
        try:
            response = await self._client.get(
                "/api/v2/user/stash",
                headers=self._headers(token),
            )
        except httpx.HTTPError as exc:
            raise ArcTrackerError("ARC Tracker request failed") from exc

        if response.status_code in {401, 403}:
            payload = {}
            try:
                parsed = response.json()
                payload = parsed if isinstance(parsed, dict) else {}
            except ValueError:
                payload = {}
            error = payload.get("error")
            code = error.get("code") if isinstance(error, dict) else ""
            if code == "missing_app_key":
                raise ArcTrackerError("ARC Tracker app key missing")
            raise ArcTrackerAuthError("Invalid ARC Tracker token")
        if response.status_code >= 400:
            raise ArcTrackerError("ARC Tracker stash request failed")
        return response.json()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()
