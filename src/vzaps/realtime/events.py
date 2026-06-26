from __future__ import annotations

import asyncio
import inspect
import json
from collections.abc import Awaitable, Callable
from typing import Any

import websockets

from vzaps.errors import VZapsRealtimeError
from vzaps.http import AsyncHttpClient, HttpClient
from vzaps.models import RealtimeEvent

EventHandler = Callable[[RealtimeEvent], Any | Awaitable[Any]]
ErrorHandler = Callable[[BaseException], Any | Awaitable[Any]]
LifecycleHandler = Callable[[], Any | Awaitable[Any]]


class EventsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def subscribe(
        self,
        *,
        instance_id: str,
        instance_token: str,
        events: list[str] | None = None,
        reconnect: bool = True,
        last_event_id: str | None = None,
        max_retries: int | None = None,
        retry_delay_seconds: float = 1.0,
    ) -> EventSubscription:
        return EventSubscription(
            self._http,
            instance_id=instance_id,
            instance_token=instance_token,
            events=events,
            reconnect=reconnect,
            last_event_id=last_event_id,
            max_retries=max_retries,
            retry_delay_seconds=retry_delay_seconds,
        )


class AsyncEventsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    def subscribe(
        self,
        *,
        instance_id: str,
        instance_token: str,
        events: list[str] | None = None,
        reconnect: bool = True,
        last_event_id: str | None = None,
        max_retries: int | None = None,
        retry_delay_seconds: float = 1.0,
    ) -> EventSubscription:
        return EventSubscription(
            self._http,
            instance_id=instance_id,
            instance_token=instance_token,
            events=events,
            reconnect=reconnect,
            last_event_id=last_event_id,
            max_retries=max_retries,
            retry_delay_seconds=retry_delay_seconds,
        )


class EventSubscription:
    def __init__(
        self,
        http: HttpClient | AsyncHttpClient,
        *,
        instance_id: str,
        instance_token: str,
        events: list[str] | None,
        reconnect: bool,
        last_event_id: str | None,
        max_retries: int | None,
        retry_delay_seconds: float,
    ) -> None:
        self._http = http
        self._instance_id = instance_id
        self._instance_token = instance_token
        self._events = events
        self._reconnect = reconnect
        self._last_event_id = last_event_id
        self._max_retries = max_retries
        self._retry_delay_seconds = retry_delay_seconds
        self._handlers: dict[str, set[EventHandler]] = {}
        self._error_handlers: set[ErrorHandler] = set()
        self._open_handlers: set[LifecycleHandler] = set()
        self._close_handlers: set[LifecycleHandler] = set()
        self._socket: Any = None
        self._task: asyncio.Task[None] | None = None
        self._closed = False
        self._retry_count = 0

    async def __aenter__(self) -> EventSubscription:
        await self.open()
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.close()

    def on(self, event: str, handler: EventHandler | None = None) -> Any:
        def decorator(func: EventHandler) -> EventHandler:
            self._handlers.setdefault(event, set()).add(func)
            return func

        if handler is None:
            return decorator
        return decorator(handler)

    def off(self, event: str, handler: EventHandler) -> EventSubscription:
        self._handlers.get(event, set()).discard(handler)
        return self

    def on_error(self, handler: ErrorHandler) -> ErrorHandler:
        self._error_handlers.add(handler)
        return handler

    def on_open(self, handler: LifecycleHandler) -> LifecycleHandler:
        self._open_handlers.add(handler)
        return handler

    def on_close(self, handler: LifecycleHandler) -> LifecycleHandler:
        self._close_handlers.add(handler)
        return handler

    async def open(self) -> None:
        if self._task and not self._task.done():
            return
        self._closed = False
        self._task = asyncio.create_task(self._run())
        await asyncio.sleep(0)

    async def close(self) -> None:
        self._closed = True
        if self._socket is not None:
            await self._socket.close()
        if self._task is not None:
            await asyncio.wait([self._task], timeout=5)

    async def wait_closed(self) -> None:
        if self._task is not None:
            await self._task

    async def _run(self) -> None:
        while not self._closed:
            try:
                await self._connect_and_receive()
                if self._closed or not self._reconnect:
                    return
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                await self._emit_error(_as_realtime_error(exc))
                if self._closed or not self._reconnect:
                    return
            if self._max_retries is not None and self._retry_count >= self._max_retries:
                return
            self._retry_count += 1
            await asyncio.sleep(min(30.0, self._retry_delay_seconds * self._retry_count))

    async def _connect_and_receive(self) -> None:
        token = await _maybe_await(self._http.get_access_token())
        url = self._http.build_realtime_url(
            "/events/ws",
            {
                "instance_id": self._instance_id,
                "events": ",".join(self._events) if self._events else None,
                "access_token": token,
                "client_token": self._http.client_token,
                "instance_token": self._instance_token,
                "last_event_id": self._last_event_id,
            },
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Client-Token": self._http.client_token,
            "X-Instance-Token": self._instance_token,
        }
        async with _connect(url, headers) as socket:
            self._socket = socket
            self._retry_count = 0
            await self._emit_lifecycle(self._open_handlers)
            async for raw in socket:
                await self._dispatch(raw)
        await self._emit_lifecycle(self._close_handlers)

    async def _dispatch(self, raw: str | bytes) -> None:
        try:
            payload = json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else raw)
            event = RealtimeEvent.model_validate(payload)
            handlers = [*self._handlers.get(event.type, set()), *self._handlers.get("All", set())]
            for handler in handlers:
                await _maybe_await(handler(event))
            await self._ack(event.id)
            self._last_event_id = event.id
        except Exception as exc:
            await self._emit_error(_as_realtime_error(exc))

    async def _ack(self, event_id: str) -> None:
        if self._socket is None or not event_id:
            return
        await self._socket.send(json.dumps({"type": "ack", "event_id": event_id}))

    async def _emit_error(self, error: BaseException) -> None:
        for handler in self._error_handlers:
            await _maybe_await(handler(error))

    async def _emit_lifecycle(self, handlers: set[LifecycleHandler]) -> None:
        for handler in handlers:
            await _maybe_await(handler())


def _connect(url: str, headers: dict[str, str]) -> Any:
    try:
        return websockets.connect(url, additional_headers=headers)
    except TypeError:
        return websockets.connect(url, extra_headers=headers)


async def _maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


def _as_realtime_error(error: Exception) -> VZapsRealtimeError:
    if isinstance(error, VZapsRealtimeError):
        return error
    return VZapsRealtimeError(str(error) or "VZaps realtime subscription failed")
