from __future__ import annotations

import os


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} before running this example")
    return value


def client_kwargs() -> dict[str, str]:
    return {
        "client_token": required_env("VZAPS_CLIENT_TOKEN"),
        "client_secret": required_env("VZAPS_CLIENT_SECRET"),
    }


def instance_id() -> str:
    return required_env("VZAPS_INSTANCE_ID")


def instance_token() -> str:
    return required_env("VZAPS_INSTANCE_TOKEN")
