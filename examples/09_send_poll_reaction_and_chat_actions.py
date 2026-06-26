from __future__ import annotations

import os

from _env import client_kwargs, instance_id, instance_token, required_env

from vzaps import VZapsClient

phone = required_env("VZAPS_PHONE")

with VZapsClient(**client_kwargs()) as client:
    print(
        client.messages.send_poll(
            instance_id=instance_id(),
            instance_token=instance_token(),
            phone=phone,
            name="Pick one",
            options=["A", "B"],
        )
    )
    message_id = os.getenv("VZAPS_MESSAGE_ID")
    if message_id:
        print(
            client.messages.react(
                instance_id=instance_id(),
                instance_token=instance_token(),
                message_id=message_id,
                reaction="+1",
            )
        )
    print(
        client.chats.archive(
            instance_id=instance_id(), instance_token=instance_token(), phone=phone
        )
    )
