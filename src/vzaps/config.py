from __future__ import annotations

from dataclasses import dataclass

import httpx

from .__about__ import __version__
from .errors import VZapsError

DEFAULT_BASE_URL = "https://api.vzaps.com"
DEFAULT_REALTIME_URL = "wss://realtime.vzaps.com"
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_TOKEN_SKEW_SECONDS = 60.0
DEFAULT_USER_AGENT = f"vzaps-python/{__version__}"


@dataclass(frozen=True, slots=True)
class VZapsConfig:
    client_token: str
    client_secret: str
    base_url: str = DEFAULT_BASE_URL
    realtime_url: str = DEFAULT_REALTIME_URL
    timeout: float | httpx.Timeout = DEFAULT_TIMEOUT_SECONDS
    limits: httpx.Limits | None = None
    token_skew_seconds: float = DEFAULT_TOKEN_SKEW_SECONDS
    user_agent: str = DEFAULT_USER_AGENT

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "client_token", _require_non_empty(self.client_token, "client_token")
        )
        object.__setattr__(
            self, "client_secret", _require_non_empty(self.client_secret, "client_secret")
        )
        object.__setattr__(self, "base_url", _normalize_base_url(self.base_url))
        object.__setattr__(self, "realtime_url", _normalize_base_url(self.realtime_url))


def _require_non_empty(value: str, name: str) -> str:
    if not value or not value.strip():
        raise VZapsError(f"VZaps {name} is required")
    return value


def _normalize_base_url(value: str) -> str:
    return value.rstrip("/")
