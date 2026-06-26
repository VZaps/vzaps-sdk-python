from __future__ import annotations

from typing import Any

import httpx

from .config import DEFAULT_USER_AGENT, VZapsConfig
from .http import AsyncHttpClient, HttpMethod
from .realtime import AsyncEventsResource
from .resources import (
    AsyncAuthResource,
    AsyncChatsResource,
    AsyncChatwootResource,
    AsyncContactsResource,
    AsyncGroupsResource,
    AsyncInstancesResource,
    AsyncMessagesResource,
    AsyncQueuesResource,
    AsyncSessionsResource,
    AsyncTypebotsResource,
    AsyncUsersResource,
    AsyncWebhooksResource,
)


class AsyncVZapsClient:
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
        http_client: httpx.AsyncClient | None = None,
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
        self._http = AsyncHttpClient(config, client=http_client)
        self.auth = AsyncAuthResource(self._http)
        self.instances = AsyncInstancesResource(self._http)
        self.sessions = AsyncSessionsResource(self._http)
        self.messages = AsyncMessagesResource(self._http)
        self.webhooks = AsyncWebhooksResource(self._http)
        self.contacts = AsyncContactsResource(self._http)
        self.groups = AsyncGroupsResource(self._http)
        self.users = AsyncUsersResource(self._http)
        self.queues = AsyncQueuesResource(self._http)
        self.typebots = AsyncTypebotsResource(self._http)
        self.chatwoot = AsyncChatwootResource(self._http)
        self.chats = AsyncChatsResource(self._http)
        self.events = AsyncEventsResource(self._http)

    async def request(
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
        return await self._http.request(
            method,
            path,
            body=body,
            query=query,
            instance_token=instance_token,
            auth=auth,
            headers=headers,
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> AsyncVZapsClient:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()
