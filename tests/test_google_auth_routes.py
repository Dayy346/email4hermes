from fastapi.testclient import TestClient

from email_assistant.api.routes.auth import get_app_settings
from email_assistant.core.config import Settings
from email_assistant.main import app

client = TestClient(app)


def test_google_auth_status_reports_missing_fields_by_default() -> None:
    response = client.get("/auth/google/status")
    assert response.status_code == 200

    payload = response.json()
    assert payload["ready"] is False
    assert payload["handoff_ready"] is False
    assert "GOOGLE_CLIENT_ID" in payload["missing_fields"]
    assert "GOOGLE_CLIENT_SECRET" in payload["missing_fields"]
    assert "GOOGLE_REFRESH_TOKEN" in payload["missing_fields"]


def test_google_auth_url_uses_settings_when_configured() -> None:
    app.dependency_overrides[get_app_settings] = lambda: Settings(
        google_client_id="client-id-123",
        google_client_secret="secret-abc",
        google_redirect_uri="http://localhost:8000/auth/google/callback",
        google_refresh_token="refresh-token-xyz",
    )
    try:
        response = client.get("/auth/google/url")
        assert response.status_code == 200
        payload = response.json()
        assert payload["ready"] is True
        assert payload["missing_fields"] == []
        assert payload["redirect_uri"] == "http://localhost:8000/auth/google/callback"
        assert payload["authorization_url"].startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    finally:
        app.dependency_overrides.clear()
