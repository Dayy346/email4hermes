from email_assistant.services.newsletter import NewsletterService, extract_links


def test_extract_links() -> None:
    text = "See https://tldr.tech/ and also https://tldr.tech/ again, plus http://example.com/a."
    links = extract_links(text)
    assert links == ["https://tldr.tech/", "http://example.com/a"]


def test_build_query_default() -> None:
    assert NewsletterService.build_query(lookback_days=3, query=None) == "in:inbox newer_than:3d"


def test_build_query_override() -> None:
    assert NewsletterService.build_query(lookback_days=3, query=" from:tldr ") == "from:tldr"


def test_newsletter_collect_demo() -> None:
    from fastapi.testclient import TestClient
    from email_assistant.main import app

    client = TestClient(app)
    response = client.post("/newsletter/collect", json={"lookback_days": 3, "max_results": 10})
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] >= 1
    assert payload["query"] == "in:inbox newer_than:3d"
    assert "links" in payload["items"][0]


def test_newsletter_send_demo() -> None:
    from fastapi.testclient import TestClient
    from email_assistant.main import app

    client = TestClient(app)
    response = client.post(
        "/newsletter/send",
        json={
            "to_email": "you@example.com",
            "subject": "Hermes Briefing",
            "body_text": "Top stories today...",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "sent"
    assert payload["to_email"] == "you@example.com"
    assert payload["message_id"] == "demo-message"


def test_newsletter_send_requires_body() -> None:
    from fastapi.testclient import TestClient
    from email_assistant.main import app

    client = TestClient(app)
    response = client.post(
        "/newsletter/send",
        json={"to_email": "you@example.com", "subject": "x", "body_text": "   "},
    )
    assert response.status_code == 400
