from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel


def dump_body(body: Any) -> Any:
    if body is None:
        return None
    if isinstance(body, BaseModel):
        return body.model_dump(by_alias=True, exclude_none=True)
    if isinstance(body, Mapping):
        return {key: dump_body(value) for key, value in body.items() if value is not None}
    if isinstance(body, list):
        return [dump_body(value) for value in body]
    if isinstance(body, tuple):
        return [dump_body(value) for value in body]
    return body


def without_keys(data: Mapping[str, Any], *keys: str) -> dict[str, Any]:
    return {
        key: dump_body(value)
        for key, value in data.items()
        if key not in keys and value is not None
    }
