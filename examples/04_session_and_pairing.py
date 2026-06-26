from __future__ import annotations

import os

from _env import client_kwargs, instance_id, instance_token

from vzaps import VZapsClient

with VZapsClient(**client_kwargs()) as client:
    print(client.sessions.status(instance_id(), instance_token=instance_token()))
    print(client.sessions.qr(instance_id(), instance_token=instance_token()))
    phone = os.getenv("VZAPS_PHONE")
    if phone:
        print(client.sessions.pair_code(instance_id(), phone, instance_token=instance_token()))
