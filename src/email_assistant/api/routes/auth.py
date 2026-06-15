from fastapi import APIRouter, Depends, HTTPException, Query

from email_assistant.core.config import Settings, get_settings
from email_assistant.integrations.google import GoogleOAuthConfig, exchange_authorization_code
from email_assistant.schemas import GoogleOAuthStatusResponse, GoogleOAuthTokenResponse

router = APIRouter(prefix="/auth/google", tags=["auth"])


def get_app_settings() -> Settings:
    return get_settings()


def _string_or_none(value: object | None) -> str | None:
    return value if isinstance(value, str) else None


def _int_or_none(value: object | None) -> int | None:
    return value if isinstance(value, int) else None


@router.get("/status", response_model=GoogleOAuthStatusResponse)
def google_auth_status(settings: Settings = Depends(get_app_settings)) -> GoogleOAuthStatusResponse:
    ready = settings.google_oauth_ready
    auth_url = None
    if ready:
        auth_url = GoogleOAuthConfig(
            client_id=settings.google_client_id or "",
            redirect_uri=settings.google_redirect_uri,
            scopes=tuple(settings.google_scope_list),
        ).authorization_url(state="handoff")

    return GoogleOAuthStatusResponse(
        ready=ready,
        handoff_ready=settings.google_handoff_ready,
        missing_fields=settings.google_missing_handoff_fields,
        client_id=settings.google_client_id,
        redirect_uri=settings.google_redirect_uri,
        scopes=settings.google_scope_list,
        authorization_url=auth_url,
    )


@router.get("/url")
def google_auth_url(settings: Settings = Depends(get_app_settings)) -> dict:
    if not settings.google_oauth_ready:
        return {
            "ready": False,
            "authorization_url": None,
            "missing_fields": settings.google_missing_handoff_fields,
        }

    auth_url = GoogleOAuthConfig(
        client_id=settings.google_client_id or "",
        redirect_uri=settings.google_redirect_uri,
        scopes=tuple(settings.google_scope_list),
    ).authorization_url(state="handoff")

    return {
        "ready": True,
        "authorization_url": auth_url,
        "missing_fields": [],
        "redirect_uri": settings.google_redirect_uri,
        "scopes": settings.google_scope_list,
    }


@router.get("/callback", response_model=GoogleOAuthTokenResponse)
def google_auth_callback(
    code: str | None = Query(default=None),
    error: str | None = Query(default=None),
    settings: Settings = Depends(get_app_settings),
) -> GoogleOAuthTokenResponse:
    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    if not settings.google_oauth_ready:
        raise HTTPException(status_code=400, detail="Google OAuth is not configured")

    raw = exchange_authorization_code(
        token_uri=settings.google_token_uri,
        client_id=settings.google_client_id or "",
        client_secret=settings.google_client_secret or "",
        code=code,
        redirect_uri=settings.google_redirect_uri,
    )

    return GoogleOAuthTokenResponse(
        access_token=_string_or_none(raw.get("access_token")),
        expires_in=_int_or_none(raw.get("expires_in")),
        refresh_token=_string_or_none(raw.get("refresh_token")),
        scope=_string_or_none(raw.get("scope")),
        token_type=_string_or_none(raw.get("token_type")),
        raw=raw,
    )
