from dataclasses import dataclass

from email_assistant.schemas import EmailMessage


class ReplyGenerator:
    def generate(self, email: EmailMessage, tone: str) -> str:
        raise NotImplementedError


@dataclass(slots=True)
class TemplateReplyGenerator(ReplyGenerator):
    default_signature: str = "Best,\nYour assistant"

    def generate(self, email: EmailMessage, tone: str) -> str:
        body_preview = email.body.strip().splitlines()[0][:180]
        tone_prefix = {
            "friendly": "Thanks for reaching out",
            "concise": "Thanks for the note",
            "professional": "Thank you for your message",
        }.get(tone.lower(), "Thanks for reaching out")

        return (
            f"Hi {email.sender.split('@')[0]},\n\n"
            f"{tone_prefix}. I saw your message about \"{email.subject}\".\n"
            f"Here is a quick reply based on your note: {body_preview}.\n\n"
            f"{self.default_signature}"
        )
