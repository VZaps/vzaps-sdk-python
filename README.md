# VZaps Python SDK

[![CI](https://github.com/VZaps/vzaps-sdk-python/actions/workflows/ci.yml/badge.svg)](https://github.com/VZaps/vzaps-sdk-python/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/vzaps.svg)](https://pypi.org/project/vzaps/)
[![Python](https://img.shields.io/pypi/pyversions/vzaps.svg)](https://pypi.org/project/vzaps/)

Official Python SDK for the VZaps public API.

## Requirements

- Python 3.10+
- `client_token` and `client_secret` from VZaps
- `instance_token` for instance-scoped operations

## Installation

```bash
pip install vzaps
```

For local development:

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from vzaps import VZapsClient

with VZapsClient(
    client_token="your-client-token",
    client_secret="your-client-secret",
) as client:
    instances = client.instances.list()
    print(instances)
```

Send a text message:

```python
from vzaps import VZapsClient

client = VZapsClient(client_token="...", client_secret="...")

client.messages.send_text(
    instance_id="VZ...",
    instance_token="instance-token",
    phone="5511999999999",
    message="Hello from Python",
)
client.close()
```

## Async

```python
from vzaps import AsyncVZapsClient

async with AsyncVZapsClient(
    client_token="your-client-token",
    client_secret="your-client-secret",
) as client:
    await client.messages.send_text(
        instance_id="VZ...",
        instance_token="instance-token",
        phone="5511999999999",
        message="Hello from async Python",
    )
```

## Authentication

The SDK exchanges `client_token` and `client_secret` for an access token using `POST /token`.
Tokens are cached and refreshed before expiration. Requests include:

- `Authorization: Bearer <access_token>`
- `X-Client-Token`
- `X-Instance-Token` when the call is scoped to an instance

## Resources

The client exposes:

- `auth`
- `instances`
- `sessions`
- `messages`
- `webhooks`
- `contacts`
- `groups`
- `users`
- `queues`
- `typebots`
- `chatwoot`
- `chats`
- `events`

All request arguments use Python `snake_case`.

## Generic Request

```python
client.request(
    "POST",
    "/instances/get",
    body={"id": "VZ..."},
)
```

## Realtime

Realtime subscriptions are async-first:

```python
async with AsyncVZapsClient(client_token="...", client_secret="...") as client:
    async with client.events.subscribe(
        instance_id="VZ...",
        instance_token="instance-token",
        events=["Message", "Connected"],
    ) as sub:
        @sub.on("Message")
        async def handle_message(event):
            print(event.id, event.data)

        await sub.wait_closed()
```

Handlers registered for `All` receive every event. The SDK sends an ack after handlers
complete and reconnects by default with `last_event_id` tracking.

## Errors

```python
from vzaps import VZapsAPIError, VZapsAuthenticationError, VZapsRateLimitError

try:
    client.instances.get("VZ...")
except VZapsAuthenticationError:
    ...
except VZapsRateLimitError:
    ...
except VZapsAPIError as exc:
    print(exc.status_code, exc.details)
```

## Documentation

See [docs.vzaps.com](https://docs.vzaps.com) for API and SDK guides.
