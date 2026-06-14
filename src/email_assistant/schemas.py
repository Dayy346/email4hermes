from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GoogleOAuthStatusResponse(BaseModel):
    ready: bool
    handoff_ready: bool
    missing_fields: list[str]
    client_id: str | None = None
    redirect_uri: str | None = None
    scopes: list[str]
    authorization_url: str | None = None


class GoogleOAuthTokenResponse(BaseModel):
    access_token: str | None = None
    expires_in: int | None = None
    refresh_token: str | None = None
    scope: str | None = None
    token_type: str | None = None
    raw: dict[str, object] | None = None


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
