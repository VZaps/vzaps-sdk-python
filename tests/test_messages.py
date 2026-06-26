from __future__ import annotations

import httpx
import pytest
import respx

from vzaps import VZapsClient


@pytest.mark.parametrize(
    ("method_name", "http_method", "suffix"),
    [
        ("send_text", "POST", "send/text"),
        ("send_image", "POST", "send/image"),
        ("send_audio", "POST", "send/audio"),
        ("send_document", "POST", "send/document"),
        ("send_video", "POST", "send/video"),
        ("send_sticker", "POST", "send/sticker"),
        ("send_gif", "POST", "send/gif"),
        ("send_location", "POST", "send/location"),
        ("send_contact", "POST", "send/contact"),
        ("send_buttons", "POST", "send/buttons"),
        ("send_list", "POST", "send/list"),
        ("send_link", "POST", "send/link"),
        ("send_poll", "POST", "send/poll"),
        ("poll_vote", "POST", "poll/vote"),
        ("react", "POST", "react"),
        ("remove_reaction", "DELETE", "react"),
        ("presence", "POST", "presence"),
        ("mark_read", "POST", "markread"),
        ("download_image", "POST", "downloadimage"),
        ("download_video", "POST", "downloadvideo"),
        ("download_audio", "POST", "downloadaudio"),
        ("download_document", "POST", "downloaddocument"),
    ],
)
@respx.mock
def test_message_methods(method_name: str, http_method: str, suffix: str) -> None:
    respx.post("https://api.vzaps.com/token").mock(
        return_value=httpx.Response(200, json={"access_token": "jwt", "expires_in": 3600})
    )
    route = respx.request(http_method, f"https://api.vzaps.com/instances/VZ1/chat/{suffix}").mock(
        return_value=httpx.Response(200, json={"ok": True})
    )
    client = VZapsClient(client_token="client", client_secret="secret")

    getattr(client.messages, method_name)(
        instance_id="VZ1",
        instance_token="it",
        phone="5511999999999",
        message="hello",
    )

    assert route.called
    client.close()
