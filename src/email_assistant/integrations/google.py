from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json

DEFAULT_GOOGLE_SCOPES: tuple[str, ...] = (
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.events",
)
GOOGLE_OAUTH_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"


@dataclass(slots=True, frozen=True)
class GoogleOAuthConfig:
    client_id: str
    redirect_uri: str
    scopes: tuple[str, ...] = DEFAULT_GOOGLE_SCOPES

    def authorization_url(self, state: str) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "include_granted_scopes": "true",
            "scope": " ".join(self.scopes),
            "state": state,
        }
        return f"{GOOGLE_OAUTH_AUTH_URL}?{urlencode(params)}"


def exchange_authorization_code(
    *,
    token_uri: str,
    client_id: str,
    client_secret: str,
    code: str,
    redirect_uri: str,
) -> dict[str, object]:
    payload = urlencode(
        {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")
    request = Request(
        token_uri,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    with urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
        return json.loads(body)
