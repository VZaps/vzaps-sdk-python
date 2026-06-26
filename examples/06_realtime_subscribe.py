from __future__ import annotations

import asyncio

from _env import client_kwargs, instance_id, instance_token

from vzaps import AsyncVZapsClient


async def main() -> None:
    async with AsyncVZapsClient(**client_kwargs()) as client:
        async with client.events.subscribe(
            instance_id=instance_id(),
            instance_token=instance_token(),
            events=["Message", "Connected", "Disconnected"],
        ) as sub:

            @sub.on("All")
            async def handle_event(event):
                print(event.type, event.id, event.data)

            await sub.wait_closed()


asyncio.run(main())
