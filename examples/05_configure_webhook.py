from __future__ import annotations

from _env import client_kwargs, instance_id, instance_token, required_env

from vzaps import VZapsClient

with VZapsClient(**client_kwargs()) as client:
    print(
        client.webhooks.set(
            instance_id=instance_id(),
            instance_token=instance_token(),
            url=required_env("VZAPS_WEBHOOK_URL"),
            enabled=True,
            events=["Message", "Connected", "Disconnected"],
        )
    )
