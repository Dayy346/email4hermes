from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Literal, Protocol

from email_assistant.core.config import Settings, get_settings
from email_assistant.integrations.google import GoogleGmailProvider
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
class GmailEmailProvider:
    settings: Settings = field(default_factory=get_settings)
    _client: GoogleGmailProvider | None = field(default=None, init=False, repr=False)

    def _gmail_client(self) -> GoogleGmailProvider:
        if self._client is None:
            self._client = GoogleGmailProvider(
                client_id=self.settings.google_client_id or "",
                client_secret=self.settings.google_client_secret or "",
                refresh_token=self.settings.google_refresh_token or "",
                token_uri=self.settings.google_token_uri,
            )
        return self._client

    @staticmethod
    def _from_raw(raw: dict[str, object]) -> EmailMessage:
        received_at = raw.get("received_at")
        status = raw.get("status")
        thread_id = raw.get("thread_id")
        if isinstance(status, str) and status in {"unread", "read", "replied", "sent"}:
            status_value: Literal["unread", "read", "replied", "sent"] = status  # type: ignore[assignment]
        else:
            status_value = "read"
        return EmailMessage(
            id=str(raw.get("id", "")),
            sender=str(raw.get("sender", "unknown@example.com")),
            subject=str(raw.get("subject", "(no subject)")),
            body=str(raw.get("body", "")),
            received_at=received_at if isinstance(received_at, datetime) else datetime.now(tz=UTC),
            status=status_value,
            thread_id=thread_id if isinstance(thread_id, str) else None,
        )

    @staticmethod
    def _split_sender(sender: str) -> tuple[str, str]:
        sender = sender.strip()
        if "<" in sender and ">" in sender:
            name_part, email_part = sender.split("<", 1)
            return name_part.strip() or email_part.rstrip(">"), email_part.rstrip("> ")
        return sender, sender

    def list_emails(self) -> list[EmailMessage]:
        return [self._from_raw(raw) for raw in self._gmail_client().list_messages()]

    def get_email(self, email_id: str) -> EmailMessage | None:
        try:
            return self._from_raw(self._gmail_client().get_message(email_id))
        except Exception:
            return None

    def create_draft_reply(self, email_id: str, draft: str) -> EmailMessage:
        email = self.get_email(email_id)
        if email is None:
            raise KeyError(email_id)
        email.status = "read"
        return email.model_copy()

    def send_reply(self, email_id: str, reply_text: str) -> EmailMessage:
        email = self.get_email(email_id)
        if email is None:
            raise KeyError(email_id)

        self._gmail_client().send_reply(
            thread_id=email.thread_id,
            to_email=self._split_sender(email.sender)[1],
            subject=email.subject,
            body_text=reply_text,
        )
        email.status = "sent"
        return email.model_copy()


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
