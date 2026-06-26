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


JsonBody = dict[str, Any] | VZapsModel
JsonDict = dict[str, Any]
