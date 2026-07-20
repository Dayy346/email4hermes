from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
import re

from email_assistant.core.config import Settings, get_settings
from email_assistant.integrations.google import GoogleGmailProvider
from email_assistant.schemas import NewsletterItem
from email_assistant.services.email import EmailMessage, InMemoryEmailProvider

_LINK_RE = re.compile(r"https?://[^\s<>\"')\]]+", re.IGNORECASE)


def extract_links(text: str) -> list[str]:
    seen: set[str] = set()
    links: list[str] = []
    for match in _LINK_RE.findall(text or ""):
        cleaned = match.rstrip(".,;:!?)")
        if cleaned not in seen:
            seen.add(cleaned)
            links.append(cleaned)
    return links


@dataclass(slots=True)
class NewsletterService:
    settings: Settings = field(default_factory=get_settings)
    _client: GoogleGmailProvider | None = field(default=None, init=False, repr=False)
    _demo_provider: InMemoryEmailProvider = field(default_factory=InMemoryEmailProvider)

    def _gmail_ready(self) -> bool:
        return (
            self.settings.email_backend.lower() == "gmail"
            and self.settings.google_handoff_ready
        )

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
    def build_query(*, lookback_days: int, query: str | None) -> str:
        if query and query.strip():
            return query.strip()
        return f"in:inbox newer_than:{lookback_days}d"

    def collect(
        self,
        *,
        lookback_days: int = 3,
        max_results: int = 25,
        query: str | None = None,
    ) -> tuple[list[NewsletterItem], str]:
        resolved_query = self.build_query(lookback_days=lookback_days, query=query)

        if self._gmail_ready():
            raw_items = self._gmail_client().list_messages(
                max_results=max_results,
                query=resolved_query,
            )
            items = [self._from_raw(raw) for raw in raw_items]
            return items, resolved_query

        demo_emails = self._demo_provider.list_emails()[:max_results]
        items = [self._from_email(email) for email in demo_emails]
        return items, resolved_query

    def send(self, *, to_email: str, subject: str, body_text: str) -> dict[str, object]:
        if not self._gmail_ready():
            return {
                "id": "demo-message",
                "status": "sent",
                "to_email": to_email,
                "subject": subject,
                "demo": True,
            }

        result = self._gmail_client().send_message(
            to_email=to_email,
            subject=subject,
            body_text=body_text,
        )
        return result

    @staticmethod
    def _from_raw(raw: dict[str, object]) -> NewsletterItem:
        received_at = raw.get("received_at")
        body = str(raw.get("body", ""))
        return NewsletterItem(
            id=str(raw.get("id", "")),
            sender=str(raw.get("sender", "unknown@example.com")),
            subject=str(raw.get("subject", "(no subject)")),
            body=body,
            links=extract_links(body),
            received_at=received_at if isinstance(received_at, datetime) else datetime.now(tz=UTC),
        )

    @staticmethod
    def _from_email(email: EmailMessage) -> NewsletterItem:
        return NewsletterItem(
            id=email.id,
            sender=email.sender,
            subject=email.subject,
            body=email.body,
            links=extract_links(email.body),
            received_at=email.received_at,
        )
