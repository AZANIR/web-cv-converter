from functools import lru_cache

from pydantic import field_validator, model_validator
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
    # Optional provider fallback order, comma-separated (e.g. anthropic)
    ai_fallback_providers: str = ""
    gemini_api_key: str = ""
    # Priority-ordered list (comma-separated). First available model wins.
    gemini_models: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_fallback_models: str = ""
    gemini_retry_on_503: bool = True
    gemini_retry_on_429: bool = False
    gemini_max_output_tokens: int = 65536
    gemini_attempt_timeout_seconds: int = 45
    conversion_ai_timeout_seconds: int = 90
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"
    anthropic_max_tokens: int = 4096
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4.1-mini"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_timeout_seconds: int = 60
    allowed_origins: str = "http://localhost:3000"
    # Comma-separated emails that receive admin (UI + /api/admin/*) without profiles.role in DB.
    admin_emails: str = ""

    # Embedding
    embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = 3072

    max_upload_bytes: int = 5 * 1024 * 1024
    conversions_per_hour: int = 10
    signed_url_expires_seconds: int = 3600
    log_level: str = "INFO"
    log_file_path: str = "/app/logs/backend.log"
    log_max_bytes: int = 10 * 1024 * 1024
    log_backup_count: int = 5

    @model_validator(mode="after")
    def check_required_in_production(self) -> "Settings":
        import os

        if os.getenv("ENVIRONMENT", "").lower() == "production":
            required = {
                "auth0_domain": self.auth0_domain,
                "auth0_api_audience": self.auth0_api_audience,
                "supabase_url": self.supabase_url,
                "supabase_service_role_key": self.supabase_service_role_key,
            }
            missing = [k for k, v in required.items() if not v]
            if missing:
                raise ValueError(
                    f"Missing required config in production: {', '.join(missing)}"
                )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
