from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class VZapsModel(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class EventType(str, Enum):
    MESSAGE = "Message"
    READ_RECEIPT = "ReadReceipt"
    PRESENCE = "Presence"
    CHAT_PRESENCE = "ChatPresence"
    HISTORY_SYNC = "HistorySync"
    CONNECTED = "Connected"
    DISCONNECTED = "Disconnected"
    GROUP_PARTICIPANTS_ADD = "GroupParticipantsAdd"
    GROUP_PARTICIPANTS_REMOVE = "GroupParticipantsRemove"
    ALL = "All"


class RealtimeEvent(VZapsModel):
    id: str
    type: str
    instance_id: str | None = None
    created_at: datetime | str | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class SessionBusinessCategory(VZapsModel):
    id: str
    name: str


class SessionBusinessProfile(VZapsModel):
    business_hours_timezone: str | None = None
    categories: list[SessionBusinessCategory] | None = None
    profile_options: dict[str, str] | None = None
    address: str | None = None
    email: str | None = None


class SessionStatusData(VZapsModel):
    connected: bool
    phone: str | None = None
    whatsapp_jid: str | None = None
    push_name: str | None = None
    business_name: str | None = None
    business_profile: SessionBusinessProfile | None = None
    profile_picture_id: str | None = None
    profile_picture_url: str | None = None
    profile_url: str | None = None
    verified_name: str | None = None
    about: str | None = None
    website: str | None = None


class SessionStatusResponse(VZapsModel):
    code: int
    success: bool
    data: SessionStatusData


JsonBody = dict[str, Any] | VZapsModel
JsonDict = dict[str, Any]
