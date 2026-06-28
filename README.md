# VZaps Python SDK

[![CI](https://github.com/VZaps/vzaps-sdk-python/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/VZaps/vzaps-sdk-python/actions/workflows/ci.yml) [![SDK Documentation](https://img.shields.io/badge/SDK-Documentation-blue)](https://docs.vzaps.com/en/sdk/python/installation) [![license](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![PyPI](https://img.shields.io/pypi/v/vzaps.svg?logo=pypi&logoColor=white)](https://pypi.org/project/vzaps/)
[![Python](https://img.shields.io/pypi/pyversions/vzaps.svg?logo=python&logoColor=white)](https://pypi.org/project/vzaps/)

Official Python client for the [VZaps public API](https://docs.vzaps.com). Send WhatsApp messages, manage instances, configure webhooks, and subscribe to realtime events with a resource-oriented, sync and async interface.

Works in **Python 3.10+**. HTTP uses [httpx](https://www.python-httpx.org/); WebSocket realtime uses [websockets](https://websockets.readthedocs.io/).

---

## Table of contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Authentication](#authentication)
- [Configuration](#configuration)
- [Resources](#resources)
- [Instance tokens](#instance-tokens)
- [Webhooks](#webhooks)
- [Realtime events](#realtime-events)
- [Error handling](#error-handling)
- [Python](#python)
- [Documentation](#documentation)

---

## Features

- **Automatic JWT handling** — exchanges `client_token` + `client_secret` for a bearer token and refreshes it before expiry.
- **Resource-oriented API** — `instances`, `messages`, `webhooks`, `contacts`, `groups`, and `events` mirror the public HTTP contract.
- **Sync and async clients** — `VZapsClient` and `AsyncVZapsClient` share the same resource surface.
- **Realtime WebSocket client** — subscribe to instance events with reconnect, resume (`last_event_id`), and server-side ack.
- **Instance token support** — pass `instance_token` on each instance-scoped request.
- **Extensible transport** — inject a custom `httpx.Client` or `httpx.AsyncClient` for tests or custom runtimes.

---

## Requirements

| Runtime | Minimum version |
| --- | --- |
| Python | 3.10+ |

The SDK uses `httpx` for HTTP. No extra HTTP dependency is required beyond the package itself.

---

## Installation

```bash
pip install vzaps
```

---

## Quick start

Create credentials in the [VZaps dashboard](https://docs.vzaps.com) (`client_token` and `client_secret`), then send a text message:

```python
from vzaps import VZapsClient

with VZapsClient(
    client_token="your-client-token",
    client_secret="your-client-secret",
) as client:
    client.messages.send_text(
        instance_id="VZKB8AU4S4CWY1SLXX4I5WJGRZQMDDFTV6",
        instance_token="instance-token",
        phone="5511999999999",
        message="Hello from VZaps",
    )
```

Async equivalent:

```python
from vzaps import AsyncVZapsClient

async with AsyncVZapsClient(
    client_token="your-client-token",
    client_secret="your-client-secret",
) as client:
    await client.messages.send_text(
        instance_id="VZKB8AU4S4CWY1SLXX4I5WJGRZQMDDFTV6",
        instance_token="instance-token",
        phone="5511999999999",
        message="Hello from VZaps",
    )
```

---

## Authentication

VZaps uses a two-step model:

1. **Account credentials** — `client_token` and `client_secret` identify your integration. The SDK calls `POST /token` and caches the JWT.
2. **Instance token** — instance-scoped routes also require `X-Instance-Token`. Pass it on each instance-scoped request (see [Instance tokens](#instance-tokens)).

Every authenticated HTTP request sends:

| Header | Value |
| --- | --- |
| `Authorization` | `Bearer <jwt>` |
| `X-Client-Token` | Your client token |
| `X-Instance-Token` | Instance token, on instance-scoped requests |

You rarely need to call `auth.get_access_token()` directly — resources attach the token for you. Use it when integrating with custom HTTP logic:

```python
token = client.auth.get_access_token()
```

---

## Configuration

The SDK connects to the VZaps production platform automatically:

| Service | Endpoint |
| --- | --- |
| REST API | `https://api.vzaps.com` |
| Realtime WebSocket | `wss://realtime.vzaps.com/events/ws` |

Pass options to `VZapsClient(...)` or `AsyncVZapsClient(...)`:

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `client_token` | `str` | — | **Required.** Public client token from the dashboard. |
| `client_secret` | `str` | — | **Required.** Client secret used to obtain JWTs. |
| `base_url` | `str` | `https://api.vzaps.com` | REST API base URL. |
| `realtime_url` | `str` | `wss://realtime.vzaps.com` | Realtime WebSocket base URL. |
| `timeout` | `float` \| `httpx.Timeout` | `30.0` | HTTP request timeout in seconds. |
| `token_skew_seconds` | `float` | `60.0` | Refresh JWT this many seconds before expiry. |
| `limits` | `httpx.Limits` | — | Optional httpx connection pool limits. |
| `user_agent` | `str` | package default | Optional `User-Agent` header on HTTP requests. |
| `http_client` | `httpx.Client` \| `httpx.AsyncClient` | — | Custom httpx client (tests, proxies, tracing). |

No host configuration is required — install the package, pass your credentials, and the client targets the production API and realtime service.

---

## Resources

The client exposes namespaced resources. Responses are decoded as Python objects (typically `dict`/`list`) so you can align with the [OpenAPI schema](https://docs.vzaps.com/api-reference).

### `client.instances`

| Method | HTTP | Description |
| --- | --- | --- |
| `create(request?)` | `PUT /instances/create` | Create a WhatsApp instance. |
| `list(request?)` | `POST /instances/list` | List instances (pagination, search, sort). |
| `get(instance_id)` | `POST /instances/get` | Get instance details. |
| `update(instance_id, request?, *, instance_token?)` | `PATCH /instances/:id` | Update instance settings. |
| `restart(instance_id, *, instance_token?)` | `POST /instances/:id/restart` | Restart instance runtime. |

### `client.messages`

`client.messages` wraps the public WhatsApp send and chat endpoints. The most common calls are shown below; the SDK also exposes the other public message operations documented in the API reference, including media, interactive messages, reactions, polls, downloads, edits, deletes, presence, and read receipts.

```python
client.messages.send_text(
    instance_id="VZ...",
    instance_token="instance-token",
    phone="5511999999999",
    message="Hello",
)

client.messages.send_image(
    instance_id="VZ...",
    instance_token="instance-token",
    phone="5511999999999",
    image="https://example.com/photo.jpg",
    caption="Check this out",
)
```

Available send helpers include `send_text`, `send_image`, `send_audio`, `send_document`, `send_video`, `send_sticker`, `send_gif`, `send_location`, `send_contact`, `send_buttons`, `send_list`, `send_link`, and `send_poll`. See the API documentation for complete payload examples.

### `client.webhooks`

| Method | HTTP | Description |
| --- | --- | --- |
| `get(instance_id, *, instance_token?)` | `GET /instances/:id/webhook` | Read current webhook configuration. |
| `set(request)` | `POST /instances/:id/webhook` | Configure webhook URL and subscribed events. |

### `client.contacts`

| Method | HTTP | Description |
| --- | --- | --- |
| `list(instance_id, *, instance_token?)` | `GET /instances/:id/contact/list` | List contacts for the instance. |
| `add(request)` | `POST /instances/:id/contact/add` | Add a contact. |

### `client.groups`

| Method | HTTP | Description |
| --- | --- | --- |
| `list(request)` | `GET /instances/:id/group/list` | List groups (paginated). |
| `get(request)` | `GET /instances/:id/group/info` | Get group metadata by `group_id`. |

### `client.sessions`

| Method | HTTP | Description |
| --- | --- | --- |
| `status(instance_id, *, instance_token=...)` | `GET /instances/:id/session/status` | Check WhatsApp login state and, when connected, live profile fields. |

`GET /instances/{id}/session/status` returns `SessionStatusResponse`. When `data.connected` is `true`, `data` includes (in order) `phone`, `whatsapp_jid`, `push_name`, `business_name`, `business_profile`, `profile_picture_id`, `profile_picture_url`, `profile_url`, and optional `verified_name`, `about`, `website`. When disconnected, `data` only has `connected=False`.

Other public namespaces are available as first-class resources too: `sessions`, `users`, `queues`, `typebots`, `chatwoot`, and `chats`.

### `client.request(method, path, ...)`

Escape hatch for advanced calls or newly released endpoints:

```python
instance = client.request(
    "POST",
    "/instances/get",
    body={"id": "VZ..."},
)
```

---

## Instance tokens

Instance-scoped routes require the instance token in addition to account credentials. Pass it on each request that targets an instance:

```python
client.messages.send_text(
    instance_id="VZ...",
    instance_token="instance-token",
    phone="5511999999999",
    message="Hello",
)
```

---

## Webhooks

Configure HTTP callbacks for instance events (same payload shape as realtime `data`, delivered to your URL):

```python
client.webhooks.set(
    instance_id="VZ...",
    instance_token="instance-token",
    webhook_url="https://example.com/webhooks/vzaps",
    events=["Message", "Connected", "Disconnected"],
)
```

Common event types: `Message`, `ReadReceipt`, `Connected`, `Disconnected`, `Presence`, `ChatPresence`, `HistorySync`, `GroupParticipantsAdd`, `GroupParticipantsRemove`, or `All`.

Event payloads (webhook and realtime) use **snake_case**, matching the platform. Incoming media events include `media_url` inside `data` when platform storage is available.

---

## Realtime events

Subscribe to the same events over WebSocket at **`wss://realtime.vzaps.com`**. This is the recommended path for in-app notifications, bots, and dashboards that need low-latency delivery without exposing a public webhook URL.

Realtime subscriptions are async-first. Use `AsyncVZapsClient` and `async with client.events.subscribe(...)`:

```python
async with AsyncVZapsClient(
    client_token="...",
    client_secret="...",
) as client:
    async with client.events.subscribe(
        instance_id="VZ...",
        instance_token="instance-token",
        events=["Message", "Connected", "Disconnected"],
        reconnect=True,
        last_event_id="evt_previous_id",  # optional resume after disconnect
    ) as sub:

        @sub.on_open
        async def on_open() -> None:
            print("Connected to realtime")

        @sub.on("Message")
        async def on_message(event) -> None:
            print(event.data)

        @sub.on_error
        async def on_error(error) -> None:
            print(error)

        await sub.wait_closed()
```

### Event envelope

Each WebSocket message keeps the platform shape (`snake_case`):

```json
{
  "id": "evt_…",
  "type": "Message",
  "instance_id": "VZ…",
  "created_at": "2026-06-23T22:57:17.000Z",
  "data": {
    "type": "Message",
    "event": { },
    "media_url": "https://…"
  }
}
```

- **`data`** — same payload as webhook delivery (`snake_case`).
- **`media_url`** — present on incoming media messages when platform storage is available.

### Delivery and ack

Delivery is **at-least-once**. After your handler runs, the SDK sends an ack automatically on the WebSocket connection. Use `last_event_id` when reconnecting if you need to reduce gaps. Deduplicate on `event.id` in your application if you process events idempotently.

### Subscribe options

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `instance_id` | `str` | — | **Required.** Instance to watch. |
| `events` | `list[str]` | all subscribed | Comma-filtered event types. |
| `instance_token` | `str` | — | **Required.** Instance token for authorization. |
| `reconnect` | `bool` | `True` | Reconnect after socket close. |
| `max_retries` | `int` | unlimited | Max reconnect attempts. |
| `retry_delay_seconds` | `float` | `1.0` | Delay between reconnects. |
| `last_event_id` | `str` | — | Resume cursor after disconnect. |

### Handler registration

| Method | When it fires |
| --- | --- |
| `on_open(...)` | WebSocket connected. |
| `on_close(...)` | WebSocket closed. |
| `on_error(...)` | Handler or transport error. |
| `on("Message", ...)` | Matching realtime event type. |
| `on("All", ...)` | Every event type. |

---

## Error handling

The SDK raises typed exceptions you can catch and branch on:

| Class | When |
| --- | --- |
| `VZapsError` | Base class; HTTP errors include `status_code`, `code`, and `details`. |
| `VZapsAuthenticationError` | Invalid `client_token` / `client_secret` (401). |
| `VZapsTimeoutError` | Request exceeded `timeout`. |
| `VZapsRateLimitError` | Rate limited (429). |
| `VZapsAPIError` | Other non-2xx API responses. |
| `VZapsRealtimeError` | Realtime handler or transport failures. |

```python
from vzaps import (
    VZapsAPIError,
    VZapsAuthenticationError,
    VZapsError,
    VZapsRateLimitError,
    VZapsTimeoutError,
)

try:
    client.messages.send_text(
        instance_id="VZ...",
        instance_token="instance-token",
        phone="5511999999999",
        message="Hello",
    )
except VZapsAuthenticationError:
    print("Check client credentials")
except VZapsTimeoutError:
    print("Request timed out")
except VZapsRateLimitError:
    print("Rate limited")
except VZapsAPIError as exc:
    print(exc.status_code, exc.message, exc.details)
except VZapsError:
    raise
```

---

## Python

The package uses **snake_case** for Python APIs and request keyword arguments. **Realtime and webhook event payloads stay in snake_case** so both delivery channels match the platform wire format.

Resources accept dict payloads and keyword arguments, which makes it easy to pass newly released API fields before typed helpers are added:

```python
client.messages.send_image(
    instance_id="VZ...",
    instance_token="instance-token",
    phone="5511999999999",
    image="https://example.com/photo.jpg",
    caption="Check this out",
)

page = client.instances.list(page=1, size=20, search="support")
```

Use `client.request(...)` when you need full control over method, path, and body.

---

## Documentation

- [VZaps docs](https://docs.vzaps.com)
- [API reference (OpenAPI)](https://docs.vzaps.com/api-reference)
- [Postman collections](https://docs.vzaps.com/postman/)
- [Report an issue](https://github.com/VZaps/vzaps-sdk-python/issues)

---

## License

MIT © VZaps
