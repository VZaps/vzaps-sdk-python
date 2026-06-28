from __future__ import annotations

from typing import Any

from vzaps.http import HttpClient, HttpMethod
from vzaps.models import SessionStatusResponse

from ._helpers import body_or_none, merge_request, quote_path, split_instance_request


class AuthResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get_access_token(self) -> str:
        return self._http.get_access_token()


class InstancesResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(self, request: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        return self._http.request("PUT", "/instances/create", body=merge_request(request, **kwargs))

    def list(self, request: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        page = data.get("page", 1)
        size = data.get("size") or data.get("page_size") or data.get("pageSize") or 20
        search = data.get("search")
        filter_value = dict(data.get("filter") or {})
        if isinstance(search, str) and search.strip():
            filter_value["query"] = search.strip()
        body = {
            "page": page,
            "size": size,
            "filter": filter_value,
            "sort": data.get("sort"),
            "sort_desc": data.get("sort_desc", data.get("sortDesc")),
        }
        return self._http.request("POST", "/instances/list", body=body)

    def get(self, instance_id: str) -> Any:
        return self._http.request("POST", "/instances/get", body={"id": instance_id})

    def update(
        self,
        instance_id: str,
        request: dict[str, Any] | None = None,
        *,
        instance_token: str | None = None,
        **kwargs: Any,
    ) -> Any:
        return self._http.request(
            "PATCH",
            f"/instances/{quote_path(instance_id)}",
            body=merge_request(request, **kwargs),
            instance_token=instance_token,
        )

    def restart(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return self._http.request(
            "POST", f"/instances/{quote_path(instance_id)}/restart", instance_token=instance_token
        )

    def delete(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return self._http.request(
            "DELETE", f"/instances/{quote_path(instance_id)}", instance_token=instance_token
        )

    def provision(self, request: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        return self._http.request(
            "PUT", "/instances/provision", body=merge_request(request, **kwargs)
        )

    def search(self, request: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        return self._http.request(
            "POST", "/instances/search", body=merge_request(request, **kwargs)
        )

    def subscribe(
        self,
        instance_id: str,
        request: dict[str, Any] | None = None,
        *,
        instance_token: str | None = None,
        **kwargs: Any,
    ) -> Any:
        return self._http.request(
            "POST",
            f"/instances/{quote_path(instance_id)}/subscribe",
            body=merge_request(request, **kwargs),
            instance_token=instance_token,
        )

    def resume_subscription(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return self._http.request(
            "POST",
            f"/instances/{quote_path(instance_id)}/resume-subscription",
            instance_token=instance_token,
        )

    def cancel(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return self._http.request(
            "PUT", f"/instances/{quote_path(instance_id)}/cancel", instance_token=instance_token
        )


class MessagesResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def _send(self, method: HttpMethod, suffix: str, request: Any = None, **kwargs: Any) -> Any:
        instance_id, instance_token, body = split_instance_request(merge_request(request, **kwargs))
        return self._http.request(
            method,
            f"/instances/{quote_path(instance_id)}{suffix}",
            body=body_or_none(body),
            instance_token=instance_token,
        )

    def send_text(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/send/text", request, **kwargs)

    def send_image(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/send/image", request, **kwargs)

    def send_audio(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/send/audio", request, **kwargs)

    def send_document(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/send/document", request, **kwargs)

    def send_video(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/send/video", request, **kwargs)

    def send_sticker(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/send/sticker", request, **kwargs)

    def send_gif(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/send/gif", request, **kwargs)

    def send_location(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/send/location", request, **kwargs)

    def send_contact(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/send/contact", request, **kwargs)

    def send_buttons(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/send/buttons", request, **kwargs)

    def send_list(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/send/list", request, **kwargs)

    def send_link(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/send/link", request, **kwargs)

    def send_poll(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/send/poll", request, **kwargs)

    def poll_vote(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/poll/vote", request, **kwargs)

    def react(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/react", request, **kwargs)

    def remove_reaction(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("DELETE", "/chat/react", request, **kwargs)

    def presence(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/presence", request, **kwargs)

    def mark_read(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/markread", request, **kwargs)

    def download_image(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/downloadimage", request, **kwargs)

    def download_video(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/downloadvideo", request, **kwargs)

    def download_audio(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/downloadaudio", request, **kwargs)

    def download_document(self, request: Any = None, **kwargs: Any) -> Any:
        return self._send("POST", "/chat/downloaddocument", request, **kwargs)

    def edit(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        message_id = data.pop("message_id", data.pop("messageId", None))
        if not message_id:
            raise ValueError("message_id is required")
        return self._send("PATCH", f"/chat/messages/{quote_path(str(message_id))}", data)

    def delete(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        message_id = data.pop("message_id", data.pop("messageId", None))
        if not message_id:
            raise ValueError("message_id is required")
        return self._send("DELETE", f"/chat/messages/{quote_path(str(message_id))}", data)

    def send(
        self,
        instance_id: str,
        path: str,
        body: dict[str, Any],
        *,
        instance_token: str | None = None,
    ) -> Any:
        clean_path = path.lstrip("/")
        return self._http.request(
            "POST",
            f"/instances/{quote_path(instance_id)}/chat/{clean_path}",
            body=body,
            instance_token=instance_token,
        )


class WebhooksResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return self._http.request(
            "GET", f"/instances/{quote_path(instance_id)}/webhook", instance_token=instance_token
        )

    def set(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(self._http, "POST", "/webhook", merge_request(request, **kwargs))

    def search_logs(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(
            self._http, "POST", "/webhook/logs/search", merge_request(request, **kwargs)
        )

    def get_log(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        log_id = data.get("log_id") or data.get("logId")
        if not log_id:
            raise ValueError("log_id is required")
        instance_id, instance_token, _body = split_instance_request(data)
        return self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/webhook/logs/{quote_path(str(log_id))}",
            instance_token=instance_token,
        )

    def retry_log(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        log_id = data.get("log_id") or data.get("logId")
        if not log_id:
            raise ValueError("log_id is required")
        instance_id, instance_token, _body = split_instance_request(data)
        return self._http.request(
            "POST",
            f"/instances/{quote_path(instance_id)}/webhook/logs/{quote_path(str(log_id))}/retry",
            instance_token=instance_token,
        )


class ContactsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/contact/list",
            instance_token=instance_token,
        )

    def add(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(
            self._http, "POST", "/contact/add", merge_request(request, **kwargs)
        )


class GroupsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        instance_id, instance_token, body = split_instance_request(data)
        return self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/group/list",
            query={
                "page": body.get("page"),
                "page_size": body.get("page_size", body.get("pageSize")),
            },
            instance_token=instance_token,
        )

    def get(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        instance_id, instance_token, body = split_instance_request(data)
        return self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/group/info",
            query={"group_id": body.get("group_id", body.get("groupId"))},
            instance_token=instance_token,
        )

    def invite_link(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        instance_id, instance_token, body = split_instance_request(data)
        return self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/group/invitelink",
            query={
                "group_id": body.get("group_id", body.get("groupId")),
                "reset": body.get("reset"),
            },
            instance_token=instance_token,
        )

    def set_photo(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(
            self._http, "POST", "/group/photo", merge_request(request, **kwargs)
        )

    def set_name(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(
            self._http, "POST", "/group/name", merge_request(request, **kwargs)
        )

    def set_description(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(
            self._http, "POST", "/group/description", merge_request(request, **kwargs)
        )

    def set_settings(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(
            self._http, "POST", "/group/settings", merge_request(request, **kwargs)
        )

    def create(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(
            self._http, "POST", "/group/create", merge_request(request, **kwargs)
        )

    def add_admin(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(
            self._http, "POST", "/group/add-admin", merge_request(request, **kwargs)
        )

    def remove_admin(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(
            self._http, "POST", "/group/remove-admin", merge_request(request, **kwargs)
        )


class SessionsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def status(self, instance_id: str, *, instance_token: str | None = None) -> SessionStatusResponse:
        raw = self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/session/status",
            instance_token=instance_token,
        )
        return SessionStatusResponse.model_validate(raw)

    def qr(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return self._http.request(
            "GET", f"/instances/{quote_path(instance_id)}/session/qr", instance_token=instance_token
        )

    def pair_code(self, instance_id: str, phone: str, *, instance_token: str | None = None) -> Any:
        return self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/session/paircode/{quote_path(phone)}",
            instance_token=instance_token,
        )

    def disconnect(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return self._http.request(
            "POST",
            f"/instances/{quote_path(instance_id)}/session/disconnect",
            instance_token=instance_token,
        )


class UsersResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def info(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(self._http, "POST", "/user/info", merge_request(request, **kwargs))

    def check(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(
            self._http, "POST", "/user/check", merge_request(request, **kwargs)
        )

    def avatar(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(
            self._http, "POST", "/user/avatar", merge_request(request, **kwargs)
        )

    def contacts(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/user/contacts",
            instance_token=instance_token,
        )


class QueuesResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list_messages(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(
            self._http, "GET", "/queue/messages", merge_request(request, **kwargs)
        )

    def purge_messages(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(
            self._http, "DELETE", "/queue/messages", merge_request(request, **kwargs)
        )

    def remove_message(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        message_id = data.get("message_id") or data.get("messageId")
        if not message_id:
            raise ValueError("message_id is required")
        return _instance_request(
            self._http, "DELETE", f"/queue/messages/{quote_path(str(message_id))}", data
        )

    def list_operations(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(
            self._http, "GET", "/queue/operations", merge_request(request, **kwargs)
        )

    def purge_operations(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(
            self._http, "DELETE", "/queue/operations", merge_request(request, **kwargs)
        )

    def remove_operation(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        message_id = data.get("message_id") or data.get("messageId")
        if not message_id:
            raise ValueError("message_id is required")
        return _instance_request(
            self._http, "DELETE", f"/queue/operations/{quote_path(str(message_id))}", data
        )


class TypebotsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return self._http.request(
            "GET", f"/instances/{quote_path(instance_id)}/typebots", instance_token=instance_token
        )

    def create(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(self._http, "POST", "/typebots", merge_request(request, **kwargs))

    def update(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        typebot_id = data.get("typebot_id") or data.get("typebotId")
        if not typebot_id:
            raise ValueError("typebot_id is required")
        return _instance_request(
            self._http, "PATCH", f"/typebots/{quote_path(str(typebot_id))}", data
        )

    def delete(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        typebot_id = data.get("typebot_id") or data.get("typebotId")
        if not typebot_id:
            raise ValueError("typebot_id is required")
        return _instance_request(
            self._http, "DELETE", f"/typebots/{quote_path(str(typebot_id))}", data
        )

    def list_sessions(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/typebots/sessions",
            instance_token=instance_token,
        )

    def start_session(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        typebot_id = data.get("typebot_id") or data.get("typebotId")
        path = "/typebots/sessions/start"
        if typebot_id:
            path = f"/typebots/{quote_path(str(typebot_id))}/sessions/start"
        return _instance_request(self._http, "POST", path, data)

    def close_session(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        session = data.get("session")
        if not session:
            raise ValueError("session is required")
        return _instance_request(
            self._http, "POST", f"/typebots/sessions/{quote_path(str(session))}/close", data
        )

    def pause_session(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        session = data.get("session")
        if not session:
            raise ValueError("session is required")
        return _instance_request(
            self._http, "POST", f"/typebots/sessions/{quote_path(str(session))}/pause", data
        )


class ChatwootResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def get(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return self._http.request(
            "GET", f"/instances/{quote_path(instance_id)}/chatwoot", instance_token=instance_token
        )

    def set(self, request: Any = None, **kwargs: Any) -> Any:
        return _instance_request(self._http, "POST", "/chatwoot", merge_request(request, **kwargs))

    def delete(self, instance_id: str, *, instance_token: str | None = None) -> Any:
        return self._http.request(
            "DELETE",
            f"/instances/{quote_path(instance_id)}/chatwoot",
            instance_token=instance_token,
        )

    def trigger_import(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        what = data.get("what")
        if not what:
            raise ValueError("what is required")
        return _instance_request(
            self._http, "POST", f"/chatwoot/import/{quote_path(str(what))}", data
        )


class ChatsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self, request: Any = None, **kwargs: Any) -> Any:
        data = merge_request(request, **kwargs)
        instance_id, instance_token, body = split_instance_request(data)
        return self._http.request(
            "GET",
            f"/instances/{quote_path(instance_id)}/chats",
            query={
                "page": body.get("page"),
                "page_size": body.get("page_size", body.get("pageSize")),
            },
            instance_token=instance_token,
        )

    def get(self, request: Any = None, **kwargs: Any) -> Any:
        return self._chat_action("GET", "", merge_request(request, **kwargs))

    def archive(self, request: Any = None, **kwargs: Any) -> Any:
        return self._chat_action("POST", "/archive", merge_request(request, **kwargs))

    def unarchive(self, request: Any = None, **kwargs: Any) -> Any:
        return self._chat_action("POST", "/unarchive", merge_request(request, **kwargs))

    def mute(self, request: Any = None, **kwargs: Any) -> Any:
        return self._chat_action("POST", "/mute", merge_request(request, **kwargs))

    def unmute(self, request: Any = None, **kwargs: Any) -> Any:
        return self._chat_action("POST", "/unmute", merge_request(request, **kwargs))

    def pin(self, request: Any = None, **kwargs: Any) -> Any:
        return self._chat_action("POST", "/pin", merge_request(request, **kwargs))

    def unpin(self, request: Any = None, **kwargs: Any) -> Any:
        return self._chat_action("POST", "/unpin", merge_request(request, **kwargs))

    def read(self, request: Any = None, **kwargs: Any) -> Any:
        return self._chat_action("POST", "/read", merge_request(request, **kwargs))

    def unread(self, request: Any = None, **kwargs: Any) -> Any:
        return self._chat_action("POST", "/unread", merge_request(request, **kwargs))

    def clear(self, request: Any = None, **kwargs: Any) -> Any:
        return self._chat_action("POST", "/clear", merge_request(request, **kwargs))

    def delete(self, request: Any = None, **kwargs: Any) -> Any:
        return self._chat_action("DELETE", "", merge_request(request, **kwargs))

    def set_expiration(self, request: Any = None, **kwargs: Any) -> Any:
        return self._chat_action("PUT", "/expiration", merge_request(request, **kwargs))

    def _chat_action(self, method: HttpMethod, suffix: str, data: dict[str, Any]) -> Any:
        instance_id, instance_token, body = split_instance_request(data)
        phone = body.pop("phone", None)
        if not phone:
            raise ValueError("phone is required")
        return self._http.request(
            method,
            f"/instances/{quote_path(instance_id)}/chats/{quote_path(str(phone))}{suffix}",
            body=body_or_none(body),
            instance_token=instance_token,
        )


def _instance_request(
    http: HttpClient, method: HttpMethod, suffix: str, data: dict[str, Any]
) -> Any:
    instance_id, instance_token, body = split_instance_request(data)
    return http.request(
        method,
        f"/instances/{quote_path(instance_id)}{suffix}",
        body=body_or_none(body),
        instance_token=instance_token,
    )
