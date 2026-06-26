from __future__ import annotations

import json

import httpx
import pytest
import respx

from vzaps import VZapsAuthenticationError, VZapsClient, VZapsRateLimitError


@respx.mock
def test_headers_and_instance_token() -> None:
    respx.post("https://api.vzaps.com/token").mock(
        return_value=httpx.Response(200, json={"access_token": "jwt", "expires_in": 3600})
    )
    route = respx.post("https://api.vzaps.com/instances/VZ1/chat/send/text").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    client = VZapsClient(client_token="client", client_secret="secret")

    client.messages.send_text(
        instance_id="VZ1",
        instance_token="instance-secret",
        phone="5511999999999",
        message="hello",
    )

    request = route.calls.last.request
    assert request.headers["authorization"] == "Bearer jwt"
    assert request.headers["x-client-token"] == "client"
    assert request.headers["x-instance-token"] == "instance-secret"
    assert json.loads(request.content) == {"phone": "5511999999999", "message": "hello"}
    client.close()


@respx.mock
def test_auth_error_mapping() -> None:
    respx.post("https://api.vzaps.com/token").mock(
        return_value=httpx.Response(401, json={"message": "bad credentials"})
    )
    client = VZapsClient(client_token="client", client_secret="secret")
    with pytest.raises(VZapsAuthenticationError):
        client.instances.get("VZ1")
    client.close()


@respx.mock
def test_rate_limit_mapping() -> None:
    respx.post("https://api.vzaps.com/token").mock(
        return_value=httpx.Response(200, json={"access_token": "jwt", "expires_in": 3600})
    )
    respx.post("https://api.vzaps.com/instances/get").mock(
        return_value=httpx.Response(429, json={"message": "slow down"})
    )
    client = VZapsClient(client_token="client", client_secret="secret")
    with pytest.raises(VZapsRateLimitError):
        client.instances.get("VZ1")
    client.close()
