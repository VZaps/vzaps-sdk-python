from __future__ import annotations

from typing import Any

import httpx


class VZapsError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        code: str | None = None,
        details: Any = None,
        response: httpx.Response | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details
        self.response = response

    def __str__(self) -> str:
        if self.status_code is None:
            return self.message
        return f"{self.message} (status_code={self.status_code})"


class VZapsAuthenticationError(VZapsError):
    pass


class VZapsTimeoutError(VZapsError):
    pass


class VZapsRateLimitError(VZapsError):
    pass


class VZapsAPIError(VZapsError):
    pass


class VZapsRealtimeError(VZapsError):
    pass
