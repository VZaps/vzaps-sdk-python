from __future__ import annotations

import json

import httpx
import respx

from vzaps import VZapsClient


def _mock_token() -> None:
    respx.post("https://api.vzaps.com/token").mock(
        return_value=httpx.Response(200, json={"access_token": "jwt", "expires_in": 3600})
    )


@respx.mock
def test_instances_get_uses_post_body() -> None:
    _mock_token()
    route = respx.post("https://api.vzaps.com/instances/get").mock(
        return_value=httpx.Response(200, json={"id": "VZ1"})
    )
    client = VZapsClient(client_token="client", client_secret="secret")
    client.instances.get("VZ1")
    assert json.loads(route.calls.last.request.content) == {"id": "VZ1"}
    client.close()


@respx.mock
def test_main_resource_paths() -> None:
    _mock_token()
    routes = [
        respx.get("https://api.vzaps.com/instances/VZ1/webhook").mock(
            return_value=httpx.Response(200, json={})
        ),
        respx.get("https://api.vzaps.com/instances/VZ1/session/status").mock(
            return_value=httpx.Response(
                200,
                json={"code": 200, "success": True, "data": {"connected": False}},
            )
        ),
        respx.get("https://api.vzaps.com/instances/VZ1/group/list?page=1").mock(
            return_value=httpx.Response(200, json={})
        ),
        respx.delete("https://api.vzaps.com/instances/VZ1/queue/messages/m1").mock(
            return_value=httpx.Response(200, json={})
        ),
        respx.post("https://api.vzaps.com/instances/VZ1/typebots/t1/sessions/start").mock(
            return_value=httpx.Response(200, json={})
        ),
        respx.post("https://api.vzaps.com/instances/VZ1/chatwoot/import/contacts").mock(
            return_value=httpx.Response(200, json={})
        ),
        respx.post("https://api.vzaps.com/instances/VZ1/chats/5511999999999/archive").mock(
            return_value=httpx.Response(200, json={})
        ),
    ]
    client = VZapsClient(client_token="client", client_secret="secret")
    client.webhooks.get("VZ1", instance_token="it")
    client.sessions.status("VZ1", instance_token="it")
    client.groups.list(instance_id="VZ1", instance_token="it", page=1)
    client.queues.remove_message(instance_id="VZ1", instance_token="it", message_id="m1")
    client.typebots.start_session(instance_id="VZ1", instance_token="it", typebot_id="t1")
    client.chatwoot.trigger_import(instance_id="VZ1", instance_token="it", what="contacts")
    client.chats.archive(instance_id="VZ1", instance_token="it", phone="5511999999999")
    assert all(route.called for route in routes)
    client.close()
