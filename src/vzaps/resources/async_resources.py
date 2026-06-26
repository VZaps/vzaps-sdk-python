from __future__ import annotations

from typing import Any

from vzaps.http import AsyncHttpClient, HttpMethod

from ._helpers import body_or_none, merge_request, quote_path, split_instance_request


class AsyncAuthResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def get_access_token(self) -> str:
        return await self._http.get_access_token()


class AsyncInstancesResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(self, request: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        return await self._http.request(
            "PUT", "/instances/create", body=merge_request(request, **kwargs)
        )

    async def list(self, request: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        search = data.get("search")
        filter_value = dict(data.get("filter") or {})
        if isinstance(search, str) and search.strip():
            filter_value["query"] = search.strip()
        return await self._http.request(
            "POST",
            "/instances/list",
            body={
                "page": data.get("page", 1),
                "size": data.get("size") or data.get("page_size") or data.get("pageSize") or 20,
                "filter": filter_value,
                "sort": data.get("sort"),
                "sort_desc": data.get("sort_desc", data.get("sortDesc")),
            },
        )

    async def get(self, instance_id: str) -> Any:
        return await self._http.request("POST", "/instances/get", body={"id": instance_id})

    async def update(
        self,
        instance_id: str,
        request: dict[str, Any] | None = None,
        *,
        instance_token: str | None = None,
        **kwargs: Any,
    ) -> Any:
        return await self._http.request(
            "PATCH",
            f"/instances/{quote_path(instance_id)}",
            body=merge_request(request, **kwargs),
            instance_token=instance_token,
        )

    async def restart(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return await self._http.request(
            "POST", f"/instances/{quote_path(instance_id)}/restart", instance_token=instance_token
        )

    async def delete(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return await self._http.request(
            "DELETE", f"/instances/{quote_path(instance_id)}", instance_token=instance_token
        )

    async def provision(self, request: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        return await self._http.request(
            "PUT", "/instances/provision", body=merge_request(request, **kwargs)
        )

    async def search(self, request: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        return await self._http.request(
            "POST", "/instances/search", body=merge_request(request, **kwargs)
        )

    async def subscribe(
        self,
        instance_id: str,
        request: dict[str, Any] | None = None,
        *,
        instance_token: str | None = None,
        **kwargs: Any,
    ) -> Any:
        return await self._http.request(
            "POST",
            f"/instances/{quote_path(instance_id)}/subscribe",
            body=merge_request(request, **kwargs),
            instance_token=instance_token,
        )

    async def resume_subscription(
        self, instance_id: str, *, instance_token: str | None = None
    ) -> Any:
        return await self._http.request(
            "POST",
            f"/instances/{quote_path(instance_id)}/resume-subscription",
            instance_token=instance_token,
        )

    async def cancel(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return await self._http.request(
            "PUT", f"/instances/{quote_path(instance_id)}/cancel", instance_token=instance_token
        )


class AsyncMessagesResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def _send(
        self, method: HttpMethod, suffix: str, request: Any = None, **kwargs: Any
    ) -> Any:
        instance_id, instance_token, body = split_instance_request(merge_request(request, **kwargs))
        return await self._http.request(
            method,
            f"/instances/{quote_path(instance_id)}{suffix}",
            body=body_or_none(body),
            instance_token=instance_token,
        )

    async def send_text(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/send/text", request, **kwargs)

    async def send_image(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/send/image", request, **kwargs)

    async def send_audio(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/send/audio", request, **kwargs)

    async def send_document(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/send/document", request, **kwargs)

    async def send_video(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/send/video", request, **kwargs)

    async def send_sticker(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/send/sticker", request, **kwargs)

    async def send_gif(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/send/gif", request, **kwargs)

    async def send_location(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/send/location", request, **kwargs)

    async def send_contact(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/send/contact", request, **kwargs)

    async def send_buttons(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/send/buttons", request, **kwargs)

    async def send_list(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/send/list", request, **kwargs)

    async def send_link(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/send/link", request, **kwargs)

    async def send_poll(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/send/poll", request, **kwargs)

    async def poll_vote(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/poll/vote", request, **kwargs)

    async def react(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/react", request, **kwargs)

    async def remove_reaction(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("DELETE", "/chat/react", request, **kwargs)

    async def presence(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/presence", request, **kwargs)

    async def mark_read(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/markread", request, **kwargs)

    async def download_image(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/downloadimage", request, **kwargs)

    async def download_video(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/downloadvideo", request, **kwargs)

    async def download_audio(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/downloadaudio", request, **kwargs)

    async def download_document(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._send("POST", "/chat/downloaddocument", request, **kwargs)

    async def edit(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        message_id = data.pop("message_id", data.pop("messageId", None))
        if not message_id:
            raise ValueError("message_id is required")
        return await self._send("PATCH", f"/chat/messages/{quote_path(str(message_id))}", data)

    async def delete(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        message_id = data.pop("message_id", data.pop("messageId", None))
        if not message_id:
            raise ValueError("message_id is required")
        return await self._send("DELETE", f"/chat/messages/{quote_path(str(message_id))}", data)

    async def send(
        self,
        instance_id: str,
        path: str,
        body: dict[str, Any],
        *,
        instance_token: str | None = None,
    ) -> Any:
        return await self._http.request(
            "POST",
            f"/instances/{quote_path(instance_id)}/chat/{path.lstrip('/')}",
            body=body,
            instance_token=instance_token,
        )


class AsyncWebhooksResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def get(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return await self._http.request(
            "GET", f"/instances/{quote_path(instance_id)}/webhook", instance_token=instance_token
        )

    async def set(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "POST", "/webhook", merge_request(request, **kwargs)
        )

    async def search_logs(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "POST", "/webhook/logs/search", merge_request(request, **kwargs)
        )

    async def get_log(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        log_id = data.get("log_id") or data.get("logId")
        if not log_id:
            raise ValueError("log_id is required")
        instance_id, instance_token, _body = split_instance_request(data)
        return await self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/webhook/logs/{quote_path(str(log_id))}",
            instance_token=instance_token,
        )

    async def retry_log(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        log_id = data.get("log_id") or data.get("logId")
        if not log_id:
            raise ValueError("log_id is required")
        instance_id, instance_token, _body = split_instance_request(data)
        return await self._http.request(
            "POST",
            f"/instances/{quote_path(instance_id)}/webhook/logs/{quote_path(str(log_id))}/retry",
            instance_token=instance_token,
        )


class AsyncContactsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def list(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return await self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/contact/list",
            instance_token=instance_token,
        )

    async def add(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "POST", "/contact/add", merge_request(request, **kwargs)
        )


class AsyncGroupsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def list(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        instance_id, instance_token, body = split_instance_request(data)
        return await self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/group/list",
            query={
                "page": body.get("page"),
                "page_size": body.get("page_size", body.get("pageSize")),
            },
            instance_token=instance_token,
        )

    async def get(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        instance_id, instance_token, body = split_instance_request(data)
        return await self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/group/info",
            query={"group_id": body.get("group_id", body.get("groupId"))},
            instance_token=instance_token,
        )

    async def invite_link(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        instance_id, instance_token, body = split_instance_request(data)
        return await self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/group/invitelink",
            query={
                "group_id": body.get("group_id", body.get("groupId")),
                "reset": body.get("reset"),
            },
            instance_token=instance_token,
        )

    async def set_photo(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "POST", "/group/photo", merge_request(request, **kwargs)
        )

    async def set_name(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "POST", "/group/name", merge_request(request, **kwargs)
        )

    async def set_description(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "POST", "/group/description", merge_request(request, **kwargs)
        )

    async def set_settings(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "POST", "/group/settings", merge_request(request, **kwargs)
        )

    async def create(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "POST", "/group/create", merge_request(request, **kwargs)
        )

    async def add_admin(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "POST", "/group/add-admin", merge_request(request, **kwargs)
        )

    async def remove_admin(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "POST", "/group/remove-admin", merge_request(request, **kwargs)
        )


class AsyncSessionsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def status(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return await self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/session/status",
            instance_token=instance_token,
        )

    async def qr(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return await self._http.request(
            "GET", f"/instances/{quote_path(instance_id)}/session/qr", instance_token=instance_token
        )

    async def pair_code(
        self, instance_id: str, phone: str, *, instance_token: str | None = None
    ) -> Any:
        return await self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/session/paircode/{quote_path(phone)}",
            instance_token=instance_token,
        )

    async def disconnect(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return await self._http.request(
            "POST",
            f"/instances/{quote_path(instance_id)}/session/disconnect",
            instance_token=instance_token,
        )


class AsyncUsersResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def info(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "POST", "/user/info", merge_request(request, **kwargs)
        )

    async def check(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "POST", "/user/check", merge_request(request, **kwargs)
        )

    async def avatar(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "POST", "/user/avatar", merge_request(request, **kwargs)
        )

    async def contacts(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return await self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/user/contacts",
            instance_token=instance_token,
        )


class AsyncQueuesResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def list_messages(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "GET", "/queue/messages", merge_request(request, **kwargs)
        )

    async def purge_messages(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "DELETE", "/queue/messages", merge_request(request, **kwargs)
        )

    async def remove_message(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        message_id = data.get("message_id") or data.get("messageId")
        if not message_id:
            raise ValueError("message_id is required")
        return await _instance_request(
            self._http, "DELETE", f"/queue/messages/{quote_path(str(message_id))}", data
        )

    async def list_operations(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "GET", "/queue/operations", merge_request(request, **kwargs)
        )

    async def purge_operations(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "DELETE", "/queue/operations", merge_request(request, **kwargs)
        )

    async def remove_operation(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        message_id = data.get("message_id") or data.get("messageId")
        if not message_id:
            raise ValueError("message_id is required")
        return await _instance_request(
            self._http, "DELETE", f"/queue/operations/{quote_path(str(message_id))}", data
        )


class AsyncTypebotsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def list(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return await self._http.request(
            "GET", f"/instances/{quote_path(instance_id)}/typebots", instance_token=instance_token
        )

    async def create(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "POST", "/typebots", merge_request(request, **kwargs)
        )

    async def update(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        typebot_id = data.get("typebot_id") or data.get("typebotId")
        if not typebot_id:
            raise ValueError("typebot_id is required")
        return await _instance_request(
            self._http, "PATCH", f"/typebots/{quote_path(str(typebot_id))}", data
        )

    async def delete(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        typebot_id = data.get("typebot_id") or data.get("typebotId")
        if not typebot_id:
            raise ValueError("typebot_id is required")
        return await _instance_request(
            self._http, "DELETE", f"/typebots/{quote_path(str(typebot_id))}", data
        )

    async def list_sessions(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return await self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/typebots/sessions",
            instance_token=instance_token,
        )

    async def start_session(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        typebot_id = data.get("typebot_id") or data.get("typebotId")
        path = "/typebots/sessions/start"
        if typebot_id:
            path = f"/typebots/{quote_path(str(typebot_id))}/sessions/start"
        return await _instance_request(self._http, "POST", path, data)

    async def close_session(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        session = data.get("session")
        if not session:
            raise ValueError("session is required")
        return await _instance_request(
            self._http, "POST", f"/typebots/sessions/{quote_path(str(session))}/close", data
        )

    async def pause_session(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        session = data.get("session")
        if not session:
            raise ValueError("session is required")
        return await _instance_request(
            self._http, "POST", f"/typebots/sessions/{quote_path(str(session))}/pause", data
        )


class AsyncChatwootResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def get(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return await self._http.request(
            "GET", f"/instances/{quote_path(instance_id)}/chatwoot", instance_token=instance_token
        )

    async def set(self, request: Any = None, **kwargs: Any) -> Any:
        return await _instance_request(
            self._http, "POST", "/chatwoot", merge_request(request, **kwargs)
        )

    async def delete(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return await self._http.request(
            "DELETE",
            f"/instances/{quote_path(instance_id)}/chatwoot",
            instance_token=instance_token,
        )

    async def trigger_import(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        what = data.get("what")
        if not what:
            raise ValueError("what is required")
        return await _instance_request(
            self._http, "POST", f"/chatwoot/import/{quote_path(str(what))}", data
        )


class AsyncChatsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def list(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        instance_id, instance_token, body = split_instance_request(data)
        return await self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/chats",
            query={
                "page": body.get("page"),
                "page_size": body.get("page_size", body.get("pageSize")),
            },
            instance_token=instance_token,
        )

    async def get(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._chat_action("GET", "", merge_request(request, **kwargs))

    async def archive(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._chat_action("POST", "/archive", merge_request(request, **kwargs))

    async def unarchive(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._chat_action("POST", "/unarchive", merge_request(request, **kwargs))

    async def mute(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._chat_action("POST", "/mute", merge_request(request, **kwargs))

    async def unmute(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._chat_action("POST", "/unmute", merge_request(request, **kwargs))

    async def pin(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._chat_action("POST", "/pin", merge_request(request, **kwargs))

    async def unpin(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._chat_action("POST", "/unpin", merge_request(request, **kwargs))

    async def read(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._chat_action("POST", "/read", merge_request(request, **kwargs))

    async def unread(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._chat_action("POST", "/unread", merge_request(request, **kwargs))

    async def clear(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._chat_action("POST", "/clear", merge_request(request, **kwargs))

    async def delete(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._chat_action("DELETE", "", merge_request(request, **kwargs))

    async def set_expiration(self, request: Any = None, **kwargs: Any) -> Any:
        return await self._chat_action("PUT", "/expiration", merge_request(request, **kwargs))

    async def _chat_action(self, method: HttpMethod, suffix: str, data: dict[str, Any]) -> Any:
        instance_id, instance_token, body = split_instance_request(data)
        phone = body.pop("phone", None)
        if not phone:
            raise ValueError("phone is required")
        return await self._http.request(
            method,
            f"/instances/{quote_path(instance_id)}/chats/{quote_path(str(phone))}{suffix}",
            body=body_or_none(body),
            instance_token=instance_token,
        )


async def _instance_request(
    http: AsyncHttpClient, method: HttpMethod, suffix: str, data: dict[str, Any]
) -> Any:
    instance_id, instance_token, body = split_instance_request(data)
    return await http.request(
        method,
        f"/instances/{quote_path(instance_id)}{suffix}",
        body=body_or_none(body),
        instance_token=instance_token,
    )
