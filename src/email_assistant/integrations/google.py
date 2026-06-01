from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

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
