from __future__ import annotations

from _env import client_kwargs

from vzaps import VZapsClient

with VZapsClient(**client_kwargs()) as client:
    print(client.auth.get_access_token())
    print(client.instances.list(page=1, size=20))
