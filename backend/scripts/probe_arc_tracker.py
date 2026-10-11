import json
import os
import ssl
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

BASE = "https://arctracker.io"
OUT = Path(os.environ.get("PROBE_OUT", "probe-output"))
TOKEN = os.environ.get("ARC_TRACKER_API_KEY", "").strip()

ENDPOINTS = [
    "/api/v2/user/stash",
    "/api/v2/user",
    "/api/v2/items",
    "/api/v2/recipes",
    "/api/v2/hideout",
    "/api/items",
    "/api/stash",
]


def headers_for(style: str) -> dict[str, str]:
    common = {"Accept": "application/json", "User-Agent": "arc-raiders-inventory-optimizer-probe"}
    if style == "bearer":
        return {**common, "Authorization": f"Bearer {TOKEN}"}
    if style == "raw":
        return {**common, "Authorization": TOKEN}
    if style == "x-api-key":
        return {**common, "X-API-Key": TOKEN}
    return common


def fetch(url: str, headers: dict[str, str]) -> dict[str, Any]:
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=20) as resp:
            body = resp.read()[:200_000]
            parsed: Any
            try:
                parsed = json.loads(body.decode("utf-8"))
            except json.JSONDecodeError:
                parsed = body.decode("utf-8", errors="replace")[:500]
            return {"ok": True, "status": resp.status, "keys": _keys(parsed), "sample": _sample(parsed)}
    except urllib.error.HTTPError as exc:
        body = exc.read()[:1000].decode("utf-8", errors="replace")
        return {"ok": False, "status": exc.code, "body": body[:300]}
    except urllib.error.URLError as exc:
        return {"ok": False, "status": 0, "body": str(exc.reason)}


def _keys(payload: Any) -> list[str] | None:
    if isinstance(payload, dict):
        return sorted(payload.keys())
    if isinstance(payload, list) and payload and isinstance(payload[0], dict):
        return sorted(payload[0].keys())
    return None


def _sample(payload: Any) -> Any:
    if isinstance(payload, list):
        return [_redact(row) for row in payload[:5]]
    if isinstance(payload, dict):
        redacted = {}
        for key, value in list(payload.items())[:30]:
            if key.lower() in {"token", "email", "name", "username", "displayName"}:
                redacted[key] = "<redacted>"
            else:
                redacted[key] = _sample(value) if isinstance(value, (dict, list)) else value
        return redacted
    return payload


def _redact(row: Any) -> Any:
    if not isinstance(row, dict):
        return row
    keep = {}
    for key, value in row.items():
        if key.lower() in {"token", "email"}:
            keep[key] = "<redacted>"
        elif isinstance(value, (dict, list)):
            keep[key] = _sample(value)
        else:
            keep[key] = value
    return keep


def main() -> None:
    if not TOKEN:
        raise SystemExit("ARC_TRACKER_API_KEY missing")
    OUT.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {"results": []}
    for path in ENDPOINTS:
        for style in ("bearer", "raw", "x-api-key"):
            url = f"{BASE}{path}"
            result = {"path": path, "auth": style, **fetch(url, headers_for(style))}
            report["results"].append(result)
            if result.get("ok"):
                break
    (OUT / "arc_tracker_probe.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"ok_count": sum(1 for row in report["results"] if row.get("ok"))}, indent=2))


if __name__ == "__main__":
    main()
