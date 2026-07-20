from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage as MimeEmailMessage
from email.utils import format_datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json

DEFAULT_GOOGLE_SCOPES: tuple[str, ...] = (
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.events",
)
GOOGLE_OAUTH_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1"


def _http_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    data: bytes | None = None,
) -> dict[str, object]:
    request = Request(url, data=data, headers=headers or {}, method=method)
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _extract_header(payload: dict[str, object], header_name: str) -> str | None:
    headers = payload.get("headers")
    if not isinstance(headers, list):
        return None
    for header in headers:
        if not isinstance(header, dict):
            continue
        if header.get("name", "").lower() == header_name.lower():
            value = header.get("value")
            return value if isinstance(value, str) else None
    return None


def _extract_body(payload: dict[str, object]) -> str:
    body = payload.get("body")
    if isinstance(body, dict):
        data = body.get("data")
        if isinstance(data, str) and data:
            return _decode_b64url(data)

    parts = payload.get("parts")
    if isinstance(parts, list):
        for part in parts:
            if not isinstance(part, dict):
                continue
            if part.get("mimeType") == "text/plain":
                part_body = part.get("body")
                if isinstance(part_body, dict):
                    data = part_body.get("data")
                    if isinstance(data, str) and data:
                        return _decode_b64url(data)
            nested = _extract_body(part)
            if nested:
                return nested
    return ""


def _decode_b64url(data: str) -> str:
    padding = "=" * (-len(data) % 4)
    return urlsafe_b64decode((data + padding).encode("utf-8")).decode("utf-8", errors="replace")


def _parse_gmail_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(tz=UTC)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(tz=UTC)


def _build_mime_reply(*, to_email: str, subject: str, body_text: str) -> str:
    msg = MimeEmailMessage()
    msg["To"] = to_email
    msg["Subject"] = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    msg["Date"] = format_datetime(datetime.now(tz=UTC))
    msg.set_content(body_text)
    return urlsafe_b64encode(msg.as_bytes()).decode("utf-8").rstrip("=")


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


@dataclass(slots=True)
class GoogleOAuthToken:
    access_token: str
    token_type: str
    expires_in: int | None = None
    refresh_token: str | None = None
    scope: str | None = None


@dataclass(slots=True)
class GoogleOAuthClient:
    token_uri: str = GOOGLE_OAUTH_TOKEN_URL

    def exchange_authorization_code(
        self,
        *,
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
        return _http_json(
            self.token_uri,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=payload,
        )

    def refresh_access_token(self, *, client_id: str, client_secret: str, refresh_token: str) -> GoogleOAuthToken:
        payload = urlencode(
            {
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            }
        ).encode("utf-8")
        raw = _http_json(
            self.token_uri,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=payload,
        )
        access_token = raw.get("access_token")
        token_type = raw.get("token_type")
        expires_in = raw.get("expires_in")
        refresh_token_value = raw.get("refresh_token")
        scope = raw.get("scope")
        return GoogleOAuthToken(
            access_token=access_token if isinstance(access_token, str) else "",
            token_type=token_type if isinstance(token_type, str) else "Bearer",
            expires_in=expires_in if isinstance(expires_in, int) else None,
            refresh_token=refresh_token_value if isinstance(refresh_token_value, str) else None,
            scope=scope if isinstance(scope, str) else None,
        )


@dataclass(slots=True)
class GoogleGmailProvider:
    client_id: str
    client_secret: str
    refresh_token: str
    token_uri: str = GOOGLE_OAUTH_TOKEN_URL
    gmail_api_base: str = GOOGLE_GMAIL_API_BASE
    _cached_access_token: str | None = None
    _cached_expires_at: datetime | None = None

    def _access_token(self) -> str:
        now = datetime.now(tz=UTC)
        if self._cached_access_token and self._cached_expires_at and now < self._cached_expires_at:
            return self._cached_access_token

        token = GoogleOAuthClient(token_uri=self.token_uri).refresh_access_token(
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=self.refresh_token,
        )
        if not token.access_token:
            raise RuntimeError("Google OAuth refresh did not return an access token")

        self._cached_access_token = token.access_token
        ttl = max((token.expires_in or 300) - 60, 60)
        self._cached_expires_at = now + timedelta(seconds=ttl)
        return token.access_token

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._access_token()}"}

    def list_messages(self, *, max_results: int = 10) -> list[dict[str, object]]:
        query = urlencode({"maxResults": str(max_results), "labelIds": "INBOX", "q": "in:inbox"})
        data = _http_json(
            f"{self.gmail_api_base}/users/me/messages?{query}",
            headers=self._auth_headers(),
        )
        messages = data.get("messages")
        if not isinstance(messages, list):
            return []

        results: list[dict[str, object]] = []
        for message in messages:
            if not isinstance(message, dict):
                continue
            message_id = message.get("id")
            if isinstance(message_id, str):
                results.append(self.get_message(message_id))
        return results

    def get_message(self, message_id: str) -> dict[str, object]:
        data = _http_json(
            f"{self.gmail_api_base}/users/me/messages/{message_id}?format=full",
            headers=self._auth_headers(),
        )
        payload = data.get("payload")
        if not isinstance(payload, dict):
            payload = {}
        label_ids_raw = data.get("labelIds")
        label_ids = [item for item in label_ids_raw if isinstance(item, str)] if isinstance(label_ids_raw, list) else []
        sender = _extract_header(payload, "From") or "unknown@example.com"
        subject = _extract_header(payload, "Subject") or "(no subject)"
        date_value = _extract_header(payload, "Date")
        body = _extract_body(payload) or data.get("snippet", "")
        if not isinstance(body, str):
            body = ""

        return {
            "id": message_id,
            "sender": sender,
            "subject": subject,
            "body": body,
            "received_at": _parse_gmail_datetime(date_value),
            "status": "unread" if "UNREAD" in label_ids else "read",
            "thread_id": data.get("threadId") if isinstance(data.get("threadId"), str) else None,
        }

    def send_reply(self, *, thread_id: str | None, to_email: str, subject: str, body_text: str) -> dict[str, object]:
        payload: dict[str, object] = {"raw": _build_mime_reply(to_email=to_email, subject=subject, body_text=body_text)}
        if thread_id:
            payload["threadId"] = thread_id
        return _http_json(
            f"{self.gmail_api_base}/users/me/messages/send",
            method="POST",
            headers={**self._auth_headers(), "Content-Type": "application/json"},
            data=json.dumps(payload).encode("utf-8"),
        )


def exchange_authorization_code(
    *,
    token_uri: str,
    client_id: str,
    client_secret: str,
    code: str,
    redirect_uri: str,
) -> dict[str, object]:
    return GoogleOAuthClient(token_uri=token_uri).exchange_authorization_code(
        client_id=client_id,
        client_secret=client_secret,
        code=code,
        redirect_uri=redirect_uri,
    )
