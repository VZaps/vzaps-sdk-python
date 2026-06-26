from __future__ import annotations

import asyncio
import threading
import time
from dataclasses import dataclass
from typing import Any, Literal
from urllib.parse import urlencode

import httpx

from ._utils import dump_body
from .config import VZapsConfig
from .errors import VZapsAPIError, VZapsAuthenticationError, VZapsRateLimitError, VZapsTimeoutError

HttpMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"] | str


@dataclass(slots=True)
class _CachedToken:
    access_token: str
    expires_at: float


class HttpClient:
    def __init__(self, config: VZapsConfig, *, client: httpx.Client | None = None) -> None:
        self.config = config
        client_kwargs: dict[str, Any] = {"base_url": config.base_url, "timeout": config.timeout}
        if config.limits is not None:
            client_kwargs["limits"] = config.limits
        self._client = client or httpx.Client(**client_kwargs)
        self._owns_client = client is None
        self._token: _CachedToken | None = None
        self._token_lock = threading.Lock()

    @property
    def client_token(self) -> str:
        return self.config.client_token

    @property
    def realtime_url(self) -> str:
        return self.config.realtime_url

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def get_access_token(self) -> str:
        if self._has_valid_token():
            return self._token.access_token  # type: ignore[union-attr]
        with self._token_lock:
            if self._has_valid_token():
                return self._token.access_token  # type: ignore[union-attr]
            return self._request_token()

    def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        body: Any = None,
        query: dict[str, Any] | None = None,
        instance_token: str | None = None,
        auth: bool = True,
        headers: dict[str, str] | None = None,
    ) -> Any:
        request_headers = self._build_headers(
            auth=auth,
            has_body=body is not None,
            instance_token=instance_token,
            headers=headers,
        )
        try:
            response = self._client.request(
                method,
                path,
                params=_clean_query(query),
                json=dump_body(body) if body is not None else None,
                headers=request_headers,
            )
        except httpx.TimeoutException as exc:
            raise VZapsTimeoutError("VZaps request timed out") from exc
        except httpx.HTTPError as exc:
            raise VZapsAPIError(f"VZaps request failed: {exc}") from exc
        return _parse_response(response)

    def build_realtime_url(self, path: str, query: dict[str, Any] | None = None) -> str:
        clean_path = path if path.startswith("/") else f"/{path}"
        clean_query = _clean_query(query)
        suffix = f"?{urlencode(clean_query)}" if clean_query else ""
        return f"{self.config.realtime_url}{clean_path}{suffix}"

    def _has_valid_token(self) -> bool:
        return self._token is not None and self._token.expires_at > time.time()

    def _request_token(self) -> str:
        data = self.request(
            "POST",
            "/token",
            body={
                "client_token": self.config.client_token,
                "client_secret": self.config.client_secret,
            },
            auth=False,
        )
        access_token = _read_token_value(data, "access_token", "accessToken")
        expires_in = _read_token_value(data, "expires_in", "expiresIn")
        if not access_token or not expires_in:
            raise VZapsAuthenticationError(
                "VZaps token response is missing access_token or expires_in",
                details=data,
            )
        self._token = _CachedToken(
            access_token=str(access_token),
            expires_at=time.time() + float(expires_in) - self.config.token_skew_seconds,
        )
        return self._token.access_token

    def _build_headers(
        self,
        *,
        auth: bool,
        has_body: bool,
        instance_token: str | None,
        headers: dict[str, str] | None,
    ) -> dict[str, str]:
        out = {
            "Accept": "application/json",
            "User-Agent": self.config.user_agent,
        }
        if has_body:
            out["Content-Type"] = "application/json"
        if auth:
            out["Authorization"] = f"Bearer {self.get_access_token()}"
            out["X-Client-Token"] = self.config.client_token
        if instance_token:
            out["X-Instance-Token"] = instance_token
        if headers:
            out.update({key: value for key, value in headers.items() if value is not None})
        return out


class AsyncHttpClient:
    def __init__(self, config: VZapsConfig, *, client: httpx.AsyncClient | None = None) -> None:
        self.config = config
        client_kwargs: dict[str, Any] = {"base_url": config.base_url, "timeout": config.timeout}
        if config.limits is not None:
            client_kwargs["limits"] = config.limits
        self._client = client or httpx.AsyncClient(**client_kwargs)
        self._owns_client = client is None
        self._token: _CachedToken | None = None
        self._token_lock = asyncio.Lock()

    @property
    def client_token(self) -> str:
        return self.config.client_token

    @property
    def realtime_url(self) -> str:
        return self.config.realtime_url

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> AsyncHttpClient:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    async def get_access_token(self) -> str:
        if self._has_valid_token():
            return self._token.access_token  # type: ignore[union-attr]
        async with self._token_lock:
            if self._has_valid_token():
                return self._token.access_token  # type: ignore[union-attr]
            return await self._request_token()

    async def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        body: Any = None,
        query: dict[str, Any] | None = None,
        instance_token: str | None = None,
        auth: bool = True,
        headers: dict[str, str] | None = None,
    ) -> Any:
        request_headers = await self._build_headers(
            auth=auth,
            has_body=body is not None,
            instance_token=instance_token,
            headers=headers,
        )
        try:
            response = await self._client.request(
                method,
                path,
                params=_clean_query(query),
                json=dump_body(body) if body is not None else None,
                headers=request_headers,
            )
        except httpx.TimeoutException as exc:
            raise VZapsTimeoutError("VZaps request timed out") from exc
        except httpx.HTTPError as exc:
            raise VZapsAPIError(f"VZaps request failed: {exc}") from exc
        return _parse_response(response)

    def build_realtime_url(self, path: str, query: dict[str, Any] | None = None) -> str:
        clean_path = path if path.startswith("/") else f"/{path}"
        clean_query = _clean_query(query)
        suffix = f"?{urlencode(clean_query)}" if clean_query else ""
        return f"{self.config.realtime_url}{clean_path}{suffix}"

    def _has_valid_token(self) -> bool:
        return self._token is not None and self._token.expires_at > time.time()

    async def _request_token(self) -> str:
        data = await self.request(
            "POST",
            "/token",
            body={
                "client_token": self.config.client_token,
                "client_secret": self.config.client_secret,
            },
            auth=False,
        )
        access_token = _read_token_value(data, "access_token", "accessToken")
        expires_in = _read_token_value(data, "expires_in", "expiresIn")
        if not access_token or not expires_in:
            raise VZapsAuthenticationError(
                "VZaps token response is missing access_token or expires_in",
                details=data,
            )
        self._token = _CachedToken(
            access_token=str(access_token),
            expires_at=time.time() + float(expires_in) - self.config.token_skew_seconds,
        )
        return self._token.access_token

    async def _build_headers(
        self,
        *,
        auth: bool,
        has_body: bool,
        instance_token: str | None,
        headers: dict[str, str] | None,
    ) -> dict[str, str]:
        out = {
            "Accept": "application/json",
            "User-Agent": self.config.user_agent,
        }
        if has_body:
            out["Content-Type"] = "application/json"
        if auth:
            out["Authorization"] = f"Bearer {await self.get_access_token()}"
            out["X-Client-Token"] = self.config.client_token
        if instance_token:
            out["X-Instance-Token"] = instance_token
        if headers:
            out.update({key: value for key, value in headers.items() if value is not None})
        return out


def _clean_query(query: dict[str, Any] | None) -> dict[str, str]:
    return {key: str(value) for key, value in (query or {}).items() if value is not None}


def _parse_response(response: httpx.Response) -> Any:
    data = _read_response_data(response)
    if response.is_success:
        return data

    message = _read_error_message(data, response.reason_phrase or "VZaps request failed")
    code = (
        data.get("code") if isinstance(data, dict) and isinstance(data.get("code"), str) else None
    )
    kwargs = {
        "status_code": response.status_code,
        "code": code,
        "details": data,
        "response": response,
    }
    if response.status_code in {401, 403}:
        raise VZapsAuthenticationError(message, **kwargs)
    if response.status_code == 429:
        raise VZapsRateLimitError(message, **kwargs)
    raise VZapsAPIError(message, **kwargs)


def _read_response_data(response: httpx.Response) -> Any:
    if not response.content:
        return None
    content_type = response.headers.get("content-type", "")
    if "application/json" not in content_type:
        return response.text
    try:
        return response.json()
    except ValueError:
        return response.text


def _read_error_message(data: Any, fallback: str) -> str:
    if isinstance(data, dict):
        for key in ("error", "message"):
            value = data.get(key)
            if isinstance(value, str) and value:
                return value
    return fallback or "VZaps request failed"


def _read_token_value(data: Any, *keys: str) -> Any:
    if not isinstance(data, dict):
        return None
    for key in keys:
        if key in data:
            return data[key]
    return None
