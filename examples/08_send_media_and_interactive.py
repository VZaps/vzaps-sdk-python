from __future__ import annotations

from _env import client_kwargs, instance_id, instance_token, required_env

from vzaps import VZapsClient

phone = required_env("VZAPS_PHONE")

with VZapsClient(**client_kwargs()) as client:
    print(
        client.messages.send_image(
            instance_id=instance_id(),
            instance_token=instance_token(),
            phone=phone,
            image_url=required_env("VZAPS_IMAGE_URL"),
            caption="Image from Python",
        )
    )
    print(
        client.messages.send_buttons(
            instance_id=instance_id(),
            instance_token=instance_token(),
            phone=phone,
            message="Choose an option",
            buttons=[{"id": "yes", "text": "Yes"}, {"id": "no", "text": "No"}],
        )
    )
