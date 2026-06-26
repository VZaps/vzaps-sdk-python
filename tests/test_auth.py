from __future__ import annotations

import httpx
import pytest
import respx

from vzaps import VZapsClient, VZapsError


def test_requires_credentials() -> None:
    with pytest.raises(VZapsError):
        VZapsClient(client_token="", client_secret="secret")


@respx.mock
def test_token_is_cached() -> None:
    token = respx.post("https://api.vzaps.com/token").mock(
        return_value=httpx.Response(200, json={"access_token": "jwt", "expires_in": 3600})
    )
    get_instance = respx.post("https://api.vzaps.com/instances/get").mock(
        return_value=httpx.Response(200, json={"id": "VZ1"})
    )

    client = VZapsClient(client_token="client", client_secret="secret")
    assert client.instances.get("VZ1") == {"id": "VZ1"}
    assert client.instances.get("VZ1") == {"id": "VZ1"}

    assert token.call_count == 1
    assert get_instance.call_count == 2
    client.close()


@pytest.mark.asyncio
@respx.mock
async def test_async_token_is_cached() -> None:
    from vzaps import AsyncVZapsClient

    token = respx.post("https://api.vzaps.com/token").mock(
        return_value=httpx.Response(200, json={"access_token": "jwt", "expires_in": 3600})
    )
    respx.post("https://api.vzaps.com/instances/get").mock(
        return_value=httpx.Response(200, json={"id": "VZ1"})
    )

    async with AsyncVZapsClient(client_token="client", client_secret="secret") as client:
        await client.instances.get("VZ1")
        await client.instances.get("VZ1")

    assert token.call_count == 1
