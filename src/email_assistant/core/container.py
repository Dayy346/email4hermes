from dataclasses import dataclass, field

from email_assistant.services.email import EmailService, InMemoryEmailProvider
from email_assistant.services.meetings import MockMeetingScheduler
from email_assistant.services.reply import TemplateReplyGenerator


@dataclass(slots=True)
class AppContainer:
    email_service: EmailService = field(default_factory=lambda: EmailService(provider=InMemoryEmailProvider()))
    reply_generator: TemplateReplyGenerator = field(default_factory=TemplateReplyGenerator)
    meeting_scheduler: MockMeetingScheduler = field(default_factory=MockMeetingScheduler)
