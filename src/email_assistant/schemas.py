from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class EmailMessage(BaseModel):
    id: str
    sender: str
    subject: str
    body: str
    received_at: datetime
    status: Literal["unread", "read", "replied", "sent"] = "unread"
    thread_id: str | None = None


class EmailListResponse(BaseModel):
    items: list[EmailMessage]


class DraftReplyRequest(BaseModel):
    tone: str = Field(default="friendly", description="Reply tone, e.g. friendly, concise, professional")


class DraftReplyResponse(BaseModel):
    email_id: str
    draft: str


class SendReplyRequest(BaseModel):
    reply_text: str


class SendReplyResponse(BaseModel):
    email_id: str
    status: Literal["sent"]
    delivered_to: str


class ScheduleMeetingRequest(BaseModel):
    subject: str
    attendees: list[str]
    proposed_times: list[datetime]
    duration_minutes: int = Field(default=30, ge=15, le=180)
    timezone: str = "America/New_York"


class ScheduleMeetingResponse(BaseModel):
    meeting_id: str
    subject: str
    attendees: list[str]
    scheduled_time: datetime
    duration_minutes: int
    meeting_link: str
