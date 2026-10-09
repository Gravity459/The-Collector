"""Async Google Sheets client: httpx against the Sheets REST v4 API.

Auth is a service-account JWT signed locally with python-jose and exchanged
for an access token over httpx, so no sync Google SDK sits on the event loop.
"""
from __future__ import annotations

import asyncio
import base64
import binascii
import json
import time
import weakref
from typing import Any, Protocol
from urllib.parse import quote

import httpx
from jose import jwt

from app.core.config import Settings
from app.integrations.sheet_grid import Grid

SHEETS_API = "https://sheets.googleapis.com/v4/spreadsheets"
SCOPE = "https://www.googleapis.com/auth/spreadsheets"
_JWT_BEARER = "urn:ietf:params:oauth:grant-type:jwt-bearer"
_READ_RANGE = "A1:ZZ500"
_REFRESH_MARGIN_S = 60


class SheetsError(Exception):
    """Google Sheets was unreachable, refused, or misconfigured. Retryable."""


class SheetsClient(Protocol):
    async def read_grid(self) -> Grid: ...

    async def insert_columns(self, start_index: int, count: int) -> None: ...

    async def write_cell(self, a1: str, value: str | int) -> None: ...


# access tokens are plain strings, safe to share across requests and loops
_tokens: dict[str, tuple[str, float]] = {}
# an asyncio.Lock belongs to one event loop; keep one per loop
_locks: weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, asyncio.Lock] = (
    weakref.WeakKeyDictionary()
)


def _token_lock() -> asyncio.Lock:
    loop = asyncio.get_running_loop()
    lock = _locks.get(loop)
    if lock is None:
        lock = _locks[loop] = asyncio.Lock()
    return lock


def load_service_account(raw: str) -> dict[str, Any]:
    """Service-account key from env: the JSON itself, or base64 of it."""
    raw = raw.strip()
    if not raw:
        raise SheetsError("GOOGLE_SERVICE_ACCOUNT_JSON is not set")
    if not raw.startswith("{"):
        try:
            raw = base64.b64decode(raw).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError) as exc:
            raise SheetsError("GOOGLE_SERVICE_ACCOUNT_JSON is neither JSON nor base64") from exc
    try:
        info = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SheetsError("GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON") from exc
    missing = {"client_email", "private_key"} - info.keys()
    if missing:
        raise SheetsError(f"service account key is missing {', '.join(sorted(missing))}")
    return info


class GoogleSheetsClient:
    def __init__(self, http: httpx.AsyncClient, settings: Settings) -> None:
        self._http = http
        self._settings = settings
        self._sheet_id: int | None = None

    # --- auth ---------------------------------------------------------

    async def _access_token(self) -> str:
        info = load_service_account(self._settings.google_service_account_json)
        email = info["client_email"]
        cached = _tokens.get(email)
        if cached and cached[1] - _REFRESH_MARGIN_S > time.time():
            return cached[0]
        async with _token_lock():
            cached = _tokens.get(email)  # another coroutine may have refreshed
            if cached and cached[1] - _REFRESH_MARGIN_S > time.time():
                return cached[0]
            token_uri = info.get("token_uri", "https://oauth2.googleapis.com/token")
            now = int(time.time())
            assertion = jwt.encode(
                {"iss": email, "scope": SCOPE, "aud": token_uri, "iat": now, "exp": now + 3600},
                info["private_key"],
                algorithm="RS256",
                headers={"kid": info["private_key_id"]} if info.get("private_key_id") else None,
            )
            try:
                resp = await self._http.post(
                    token_uri, data={"grant_type": _JWT_BEARER, "assertion": assertion}
                )
            except httpx.HTTPError as exc:
                raise SheetsError(f"Google sign-in failed: {exc}") from exc
            if resp.status_code >= 400:
                raise SheetsError(f"Google sign-in refused ({resp.status_code}): {resp.text[:200]}")
            body = resp.json()
            _tokens[email] = (body["access_token"], now + int(body.get("expires_in", 3600)))
            return body["access_token"]

    async def _request(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        token = await self._access_token()
        try:
            resp = await self._http.request(
                method, url, headers={"Authorization": f"Bearer {token}"}, **kwargs
            )
        except httpx.HTTPError as exc:
            raise SheetsError(f"Google Sheets unreachable: {exc}") from exc
        if resp.status_code >= 400:
            try:
                message = resp.json()["error"]["message"]
            except (ValueError, KeyError, TypeError):
                message = resp.text[:200]
            raise SheetsError(f"Google Sheets error {resp.status_code}: {message}")
        return resp.json() if resp.content else {}

    # --- addressing ---------------------------------------------------

    @property
    def _base(self) -> str:
        if not self._settings.google_sheet_id or not self._settings.google_sheet_tab:
            raise SheetsError("GOOGLE_SHEET_ID / GOOGLE_SHEET_TAB are not set")
        return f"{SHEETS_API}/{self._settings.google_sheet_id}"

    def _range(self, a1: str) -> str:
        tab = self._settings.google_sheet_tab.replace("'", "''")
        return quote(f"'{tab}'!{a1}", safe="")

    async def _tab_sheet_id(self) -> int:
        if self._sheet_id is None:
            data = await self._request(
                "GET", self._base, params={"fields": "sheets.properties(sheetId,title)"}
            )
            for sheet in data.get("sheets", []):
                props = sheet.get("properties", {})
                if props.get("title") == self._settings.google_sheet_tab:
                    self._sheet_id = int(props["sheetId"])
                    break
            else:
                raise SheetsError(f"tab {self._settings.google_sheet_tab!r} not found in the sheet")
        return self._sheet_id

    # --- operations ---------------------------------------------------

    async def read_grid(self) -> Grid:
        data = await self._request(
            "GET",
            f"{self._base}/values/{self._range(_READ_RANGE)}",
            params={"valueRenderOption": "FORMATTED_VALUE", "majorDimension": "ROWS"},
        )
        rows = [[str(v) for v in row] for row in data.get("values", [])]
        width = max((len(r) for r in rows), default=0)
        return [r + [""] * (width - len(r)) for r in rows]

    async def insert_columns(self, start_index: int, count: int) -> None:
        """Insert `count` empty columns at 0-based `start_index`, copying the
        formatting of the column to their left."""
        sheet_id = await self._tab_sheet_id()
        await self._request(
            "POST",
            f"{self._base}:batchUpdate",
            json={
                "requests": [
                    {
                        "insertDimension": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": start_index,
                                "endIndex": start_index + count,
                            },
                            "inheritFromBefore": start_index > 0,
                        }
                    }
                ]
            },
        )

    async def write_cell(self, a1: str, value: str | int) -> None:
        tab = self._settings.google_sheet_tab.replace("'", "''")
        await self._request(
            "PUT",
            f"{self._base}/values/{self._range(a1)}",
            params={"valueInputOption": "RAW"},
            json={"range": f"'{tab}'!{a1}", "majorDimension": "ROWS", "values": [[value]]},
        )
