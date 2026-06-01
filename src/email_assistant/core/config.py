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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def google_scope_list(self) -> list[str]:
        return [scope for scope in self.google_scopes.split() if scope]

    @property
    def google_oauth_ready(self) -> bool:
        return bool(self.google_client_id and self.google_client_secret and self.google_redirect_uri)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
