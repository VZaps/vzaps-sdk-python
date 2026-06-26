from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx
import pytest
import respx

from vzaps import AsyncVZapsClient
from vzaps.realtime import events as realtime_events


class FakeSocket:
    def __init__(self) -> None:
        self.sent: list[str] = []
        self.closed = False
        self._messages = [
            json.dumps(
                {"id": "evt_1", "type": "Message", "instance_id": "VZ1", "data": {"body": "hi"}}
            )
        ]

    def __aiter__(self) -> FakeSocket:
        return self

    async def __anext__(self) -> str:
        if not self._messages:
            raise StopAsyncIteration
        return self._messages.pop(0)

    async def send(self, value: str) -> None:
        self.sent.append(value)

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
@respx.mock
async def test_realtime_dispatch_and_ack(monkeypatch: pytest.MonkeyPatch) -> None:
    respx.post("https://api.vzaps.com/token").mock(
        return_value=httpx.Response(200, json={"access_token": "jwt", "expires_in": 3600})
    )
    socket = FakeSocket()
    captured: dict[str, Any] = {}

    @asynccontextmanager
    async def fake_connect(url: str, headers: dict[str, str]) -> AsyncIterator[FakeSocket]:
        captured["url"] = url
        captured["headers"] = headers
        yield socket

    monkeypatch.setattr(realtime_events, "_connect", fake_connect)
    seen: list[str] = []

    async with AsyncVZapsClient(client_token="client", client_secret="secret") as client:
        sub = client.events.subscribe(
            instance_id="VZ1",
            instance_token="it",
            events=["Message"],
            reconnect=False,
            last_event_id="evt_0",
        )

        async def handle(event: Any) -> None:
            seen.append(event.id)

        sub.on("All", handle)

        async with sub:
            await asyncio.wait_for(sub.wait_closed(), timeout=1)

    assert seen == ["evt_1"]
    assert json.loads(socket.sent[0]) == {"type": "ack", "event_id": "evt_1"}
    assert "last_event_id=evt_0" in captured["url"]
    assert captured["headers"]["X-Instance-Token"] == "it"
