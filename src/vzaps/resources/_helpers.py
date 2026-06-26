from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import quote

from pydantic import BaseModel

from vzaps._utils import dump_body, without_keys


def quote_path(value: str) -> str:
    return quote(value, safe="")


def merge_request(request: Any = None, **kwargs: Any) -> dict[str, Any]:
    if request is None:
        data: dict[str, Any] = {}
    elif isinstance(request, BaseModel):
        dumped = request.model_dump(by_alias=True, exclude_none=True)
        data = dict(dumped)
    elif isinstance(request, Mapping):
        data = dict(request)
    else:
        raise TypeError("request must be a mapping or Pydantic model")
    data.update({key: value for key, value in kwargs.items() if value is not None})
    return data


def split_instance_request(request: dict[str, Any]) -> tuple[str, str | None, dict[str, Any]]:
    instance_id = request.get("instance_id") or request.get("instanceId")
    if not instance_id:
        raise ValueError("instance_id is required")
    instance_token = request.get("instance_token") or request.get("instanceToken")
    body = without_keys(request, "instance_id", "instanceId", "instance_token", "instanceToken")
    return str(instance_id), str(instance_token) if instance_token else None, body


def body_or_none(body: dict[str, Any]) -> dict[str, Any] | None:
    dumped = dump_body(body)
    return dumped if dumped else None
