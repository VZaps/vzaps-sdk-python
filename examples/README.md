# VZaps Python SDK Examples

Runnable scripts that consume the published PyPI package (`vzaps`).

You do **not** need to clone the full SDK repository to run an example. Download only the `examples/` folder, install dependencies, set environment variables, and run one script.

## Prerequisites

- Python 3.10 or later
- pip

## Option A — examples folder only (recommended)

Download only the [`examples/`](https://github.com/VZaps/vzaps-sdk-python/tree/main/examples) folder:

1. Open [examples on GitHub](https://github.com/VZaps/vzaps-sdk-python/tree/main/examples) and choose **Download ZIP**, or run:

```bash
npx --yes degit VZaps/vzaps-sdk-python/examples vzaps-python-examples
cd vzaps-python-examples
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set credentials:

```bash
export VZAPS_CLIENT_TOKEN=your-client-token
export VZAPS_CLIENT_SECRET=your-client-secret
export VZAPS_INSTANCE_ID=VZ...
export VZAPS_INSTANCE_TOKEN=your-instance-token
```

4. Run one script:

```bash
python 07_send_text_message.py
```

Shared credential loading lives in `_env.py`.

## Option B — sparse checkout

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/VZaps/vzaps-sdk-python.git
cd vzaps-sdk-python
git sparse-checkout set examples
cd examples
pip install -r requirements.txt
python 07_send_text_message.py
```

## Option C — full repository clone

```bash
git clone https://github.com/VZaps/vzaps-sdk-python.git
cd vzaps-sdk-python
pip install -e .
python examples/07_send_text_message.py
```

Use `pip install -e .` when you are developing the SDK locally.

## Examples

| File | Topic |
| --- | --- |
| `01_auth_and_list_instances.py` | Auth and instance listing |
| `02_create_instance.py` | Create instance |
| `03_instance_subscription.py` | Billing subscription |
| `04_session_and_pairing.py` | Session status, QR, and pairing code |
| `05_configure_webhook.py` | Webhook configuration |
| `06_realtime_subscribe.py` | Realtime WebSocket subscription |
| `07_send_text_message.py` | Send text message |
| `08_send_media_and_interactive.py` | Media, buttons, and list |
| `09_send_poll_reaction_and_chat_actions.py` | Poll, reaction, and chat actions |
| `10_queues.py` | Message and operation queues |
| `11_typebot_and_chatwoot.py` | TypeBot and Chatwoot |

## Coverage

- Auth and instance listing
- Instance creation and billing subscription checkout
- Session status, QR, and phone pairing code
- Webhook and realtime subscription
- Text, media, buttons, list, poll, reactions, presence
- Queue list/remove/purge examples
- TypeBot and Chatwoot integration examples
