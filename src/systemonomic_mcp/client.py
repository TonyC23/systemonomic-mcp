"""Shared HTTP client for calling the Systemonomic REST API."""
import os
import httpx
from typing import Any, Optional


DEFAULT_BASE_URL = "https://cwa-production.up.railway.app"


def _get_base_url() -> str:
    return os.environ.get("SYSTEMONOMIC_API_URL", DEFAULT_BASE_URL).rstrip("/")


def _get_api_key() -> str:
    key = os.environ.get("SYSTEMONOMIC_API_KEY", "")
    if not key:
        raise RuntimeError(
            "SYSTEMONOMIC_API_KEY is not set. "
            "Generate one at https://systemonomic.com → Profile → API Keys, "
            "then export SYSTEMONOMIC_API_KEY=sk_sys_..."
        )
    return key


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_get_api_key()}",
        "Content-Type": "application/json",
    }


async def api_get(path: str, params: Optional[dict] = None) -> Any:
    """GET request to the Systemonomic API."""
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.get(f"{_get_base_url()}{path}", headers=_headers(), params=params)
        r.raise_for_status()
        return r.json()


async def api_post(path: str, json: Optional[dict] = None) -> Any:
    """POST request to the Systemonomic API."""
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(f"{_get_base_url()}{path}", headers=_headers(), json=json or {})
        r.raise_for_status()
        return r.json()


async def api_put(path: str, json: Optional[dict] = None) -> Any:
    """PUT request to the Systemonomic API."""
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.put(f"{_get_base_url()}{path}", headers=_headers(), json=json or {})
        r.raise_for_status()
        return r.json()


async def api_delete(path: str) -> Any:
    """DELETE request to the Systemonomic API."""
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.delete(f"{_get_base_url()}{path}", headers=_headers())
        r.raise_for_status()
        return r.json()


async def api_post_blob(path: str, json: Optional[dict] = None) -> bytes:
    """POST that returns raw bytes (e.g. PDF)."""
    async with httpx.AsyncClient(timeout=180) as c:
        r = await c.post(f"{_get_base_url()}{path}", headers=_headers(), json=json or {})
        r.raise_for_status()
        return r.content
