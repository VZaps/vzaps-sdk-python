from __future__ import annotations

from _env import client_kwargs

from vzaps import VZapsClient

with VZapsClient(**client_kwargs()) as client:
    print(client.instances.create(name="Python SDK example"))
