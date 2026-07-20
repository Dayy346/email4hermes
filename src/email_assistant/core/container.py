from dataclasses import dataclass, field

from email_assistant.core.config import get_settings
from email_assistant.services.email import EmailService, GmailEmailProvider, InMemoryEmailProvider
from email_assistant.services.meetings import MockMeetingScheduler
from email_assistant.services.reply import TemplateReplyGenerator


@dataclass(slots=True)
class AppContainer:
    email_service: EmailService = field(default_factory=lambda: AppContainer._build_email_service())
    reply_generator: TemplateReplyGenerator = field(default_factory=TemplateReplyGenerator)
    meeting_scheduler: MockMeetingScheduler = field(default_factory=MockMeetingScheduler)

    @staticmethod
    def _build_email_service() -> EmailService:
        settings = get_settings()
        use_gmail = settings.email_backend.lower() == "gmail" and settings.google_handoff_ready
        provider = GmailEmailProvider() if use_gmail else InMemoryEmailProvider()
        return EmailService(provider=provider)
