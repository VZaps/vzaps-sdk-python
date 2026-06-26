from __future__ import annotations

from typing import Any

import httpx

from .config import DEFAULT_USER_AGENT, VZapsConfig
from .http import HttpClient, HttpMethod
from .realtime import EventsResource
from .resources import (
    AuthResource,
    ChatsResource,
    ChatwootResource,
    ContactsResource,
    GroupsResource,
    InstancesResource,
    MessagesResource,
    QueuesResource,
    SessionsResource,
    TypebotsResource,
    UsersResource,
    WebhooksResource,
)


class VZapsClient:
    def __init__(
        self,
        *,
        client_token: str,
        client_secret: str,
        base_url: str = "https://api.vzaps.com",
        realtime_url: str = "wss://realtime.vzaps.com",
        timeout: float | httpx.Timeout = 30.0,
        limits: httpx.Limits | None = None,
        token_skew_seconds: float = 60.0,
        user_agent: str | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        config = VZapsConfig(
            client_token=client_token,
            client_secret=client_secret,
            base_url=base_url,
            realtime_url=realtime_url,
            timeout=timeout,
            limits=limits,
            token_skew_seconds=token_skew_seconds,
            user_agent=user_agent or DEFAULT_USER_AGENT,
        )
        self._http = HttpClient(config, client=http_client)
        self.auth = AuthResource(self._http)
        self.instances = InstancesResource(self._http)
        self.sessions = SessionsResource(self._http)
        self.messages = MessagesResource(self._http)
        self.webhooks = WebhooksResource(self._http)
        self.contacts = ContactsResource(self._http)
        self.groups = GroupsResource(self._http)
        self.users = UsersResource(self._http)
        self.queues = QueuesResource(self._http)
        self.typebots = TypebotsResource(self._http)
        self.chatwoot = ChatwootResource(self._http)
        self.chats = ChatsResource(self._http)
        self.events = EventsResource(self._http)

    def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        body: Any = None,
        query: dict[str, Any] | None = None,
        instance_token: str | None = None,
        auth: bool = True,
        headers: dict[str, str] | None = None,
    ) -> Any:
        return self._http.request(
            method,
            path,
            body=body,
            query=query,
            instance_token=instance_token,
            auth=auth,
            headers=headers,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> VZapsClient:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()
