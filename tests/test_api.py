from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from email_assistant.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_emails() -> None:
    response = client.get("/emails")
    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert len(payload["items"]) >= 1


def test_draft_reply() -> None:
    response = client.post("/emails/email-1/draft", json={"tone": "professional"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["email_id"] == "email-1"
    assert "Thank you for your message" in payload["draft"]


def test_send_reply() -> None:
    response = client.post("/emails/email-1/send", json={"reply_text": "Sounds good!"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["email_id"] == "email-1"
    assert payload["status"] == "sent"


def test_schedule_meeting() -> None:
    now = datetime.now(tz=UTC)
    response = client.post(
        "/meetings/schedule",
        json={
            "subject": "Weekly check-in",
            "attendees": ["alex@example.com", "you@example.com"],
            "proposed_times": [(now + timedelta(days=1)).isoformat()],
            "duration_minutes": 30,
            "timezone": "America/New_York",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["subject"] == "Weekly check-in"
    assert payload["meeting_link"].startswith("https://meet.google.com/mock-meeting/")
