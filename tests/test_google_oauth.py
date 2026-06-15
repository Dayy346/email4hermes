from urllib.parse import parse_qs, urlparse

from email_assistant.integrations.google import DEFAULT_GOOGLE_SCOPES, GoogleOAuthConfig


def test_google_oauth_authorization_url_contains_required_params() -> None:
    config = GoogleOAuthConfig(
        client_id="client-id-123",
        redirect_uri="http://localhost:8000/auth/google/callback",
    )

    url = config.authorization_url(state="state-abc")
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    assert url.startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    assert parsed.netloc == "accounts.google.com"
    assert parsed.path == "/o/oauth2/v2/auth"
    assert params["client_id"] == ["client-id-123"]
    assert params["redirect_uri"] == ["http://localhost:8000/auth/google/callback"]
    assert params["response_type"] == ["code"]
    assert params["access_type"] == ["offline"]
    assert params["prompt"] == ["consent"]
    assert params["include_granted_scopes"] == ["true"]
    assert params["state"] == ["state-abc"]
    assert params["scope"] == [" ".join(DEFAULT_GOOGLE_SCOPES)]
