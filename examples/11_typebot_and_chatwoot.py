from __future__ import annotations

from _env import client_kwargs, instance_id, instance_token

from vzaps import VZapsClient

with VZapsClient(**client_kwargs()) as client:
    print(client.typebots.list(instance_id(), instance_token=instance_token()))
    print(client.chatwoot.get(instance_id(), instance_token=instance_token()))
