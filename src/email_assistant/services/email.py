from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Protocol
from uuid import uuid4

from email_assistant.schemas import EmailMessage


class EmailProvider(Protocol):
    def list_emails(self) -> list[EmailMessage]: ...
    def get_email(self, email_id: str) -> EmailMessage | None: ...
    def create_draft_reply(self, email_id: str, draft: str) -> EmailMessage: ...
    def send_reply(self, email_id: str, reply_text: str) -> EmailMessage: ...


@dataclass(slots=True)
class InMemoryEmailProvider:
    _emails: dict[str, EmailMessage] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self._emails:
            return
        now = datetime.now(tz=UTC)
        seed = [
            EmailMessage(
                id="email-1",
                sender="alex@example.com",
                subject="Quick intro and coffee?",
                body="Hey, are you free this week to grab coffee and talk about the product roadmap?",
                received_at=now - timedelta(hours=4),
            ),
            EmailMessage(
                id="email-2",
                sender="priya@example.com",
                subject="Design review notes",
                body="I've attached the latest design review notes. Let me know if you want to discuss them.",
                received_at=now - timedelta(days=1, hours=2),
                status="read",
            ),
            EmailMessage(
                id="email-3",
                sender="sam@example.com",
                subject="Meeting follow-up",
                body="Thanks for the meeting earlier. Can we schedule a follow-up next Tuesday afternoon?",
                received_at=now - timedelta(days=2),
            ),
        ]
        self._emails = {email.id: email for email in seed}

    def list_emails(self) -> list[EmailMessage]:
        return sorted(self._emails.values(), key=lambda item: item.received_at, reverse=True)

    def get_email(self, email_id: str) -> EmailMessage | None:
        return self._emails.get(email_id)

    def create_draft_reply(self, email_id: str, draft: str) -> EmailMessage:
        email = self.require_email(email_id)
        email.status = "read"
        return email.model_copy()

    def send_reply(self, email_id: str, reply_text: str) -> EmailMessage:
        email = self.require_email(email_id)
        email.status = "sent"
        return email.model_copy()

    def require_email(self, email_id: str) -> EmailMessage:
        email = self.get_email(email_id)
        if email is None:
            raise KeyError(email_id)
        return email


@dataclass(slots=True)
class EmailService:
    provider: EmailProvider

    def list_emails(self) -> list[EmailMessage]:
        return self.provider.list_emails()

    def get_email(self, email_id: str) -> EmailMessage | None:
        return self.provider.get_email(email_id)

    def draft_reply(self, email_id: str, draft: str) -> EmailMessage:
        return self.provider.create_draft_reply(email_id, draft)

    def send_reply(self, email_id: str, reply_text: str) -> EmailMessage:
        return self.provider.send_reply(email_id, reply_text)
