from __future__ import annotations

from _env import client_kwargs, instance_id, instance_token

from vzaps import VZapsClient

with VZapsClient(**client_kwargs()) as client:
    print(client.instances.subscribe(instance_id(), instance_token=instance_token()))
    print(client.instances.resume_subscription(instance_id(), instance_token=instance_token()))
