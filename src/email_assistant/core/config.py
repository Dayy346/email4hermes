from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from email_assistant.integrations.google import DEFAULT_GOOGLE_SCOPES


class Settings(BaseSettings):
    app_name: str = "Email Assistant"
    app_env: str = "dev"
    log_level: str = "INFO"
    default_from_email: str = "you@example.com"
    openai_api_key: str | None = None

    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    google_scopes: str = " ".join(DEFAULT_GOOGLE_SCOPES)

    # Optional handoff values for a managed Google mailbox.
    google_account_email: str | None = None
    google_refresh_token: str | None = None
    google_token_uri: str = "https://oauth2.googleapis.com/token"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def google_scope_list(self) -> list[str]:
        return [scope for scope in self.google_scopes.split() if scope]

    @property
    def google_oauth_ready(self) -> bool:
        return bool(self.google_client_id and self.google_client_secret and self.google_redirect_uri)

    @property
    def google_handoff_ready(self) -> bool:
        return self.google_oauth_ready and bool(self.google_refresh_token)

    @property
    def google_missing_handoff_fields(self) -> list[str]:
        missing: list[str] = []
        if not self.google_client_id:
            missing.append("GOOGLE_CLIENT_ID")
        if not self.google_client_secret:
            missing.append("GOOGLE_CLIENT_SECRET")
        if not self.google_redirect_uri:
            missing.append("GOOGLE_REDIRECT_URI")
        if not self.google_refresh_token:
            missing.append("GOOGLE_REFRESH_TOKEN")
        return missing


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
