from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    auth0_domain: str = ""

    @field_validator("auth0_domain", mode="before")
    @classmethod
    def normalize_auth0_domain(cls, v: object) -> object:
        if not v or not isinstance(v, str):
            return v
        s = v.strip()
        for prefix in ("https://", "http://"):
            if s.startswith(prefix):
                s = s[len(prefix) :]
        return s.rstrip("/")
    auth0_api_audience: str = ""
    # SPA Client ID: verify optional ID token for email when API access token has no email claim.
    auth0_client_id: str = ""
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    # gemini | anthropic
    ai_provider: str = "gemini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_max_output_tokens: int = 65536
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"
    anthropic_max_tokens: int = 4096
    allowed_origins: str = "http://localhost:3000"
    # Comma-separated emails that receive admin (UI + /api/admin/*) without profiles.role in DB.
    admin_emails: str = ""

    # Embedding
    embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = 3072

    max_upload_bytes: int = 5 * 1024 * 1024
    conversions_per_hour: int = 10
    signed_url_expires_seconds: int = 3600


@lru_cache
def get_settings() -> Settings:
    return Settings()
