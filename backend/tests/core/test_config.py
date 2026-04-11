from __future__ import annotations

from unittest.mock import patch

import pytest

from core.config import Settings


class TestSettings:
    def test_default_values(self):
        s = Settings(
            auth0_domain="example.auth0.com",
            supabase_url="https://fake.supabase.co",
            supabase_service_role_key="fake-key",
        )
        assert s.ai_provider == "gemini"
        assert s.max_upload_bytes == 5 * 1024 * 1024
        assert s.conversions_per_hour == 10
        assert s.signed_url_expires_seconds == 3600

    def test_normalize_auth0_domain_strips_https(self):
        s = Settings(
            auth0_domain="https://example.auth0.com/",
            supabase_url="https://fake.supabase.co",
            supabase_service_role_key="fake-key",
        )
        assert s.auth0_domain == "example.auth0.com"

    def test_normalize_auth0_domain_strips_http(self):
        s = Settings(
            auth0_domain="http://example.auth0.com",
            supabase_url="https://fake.supabase.co",
            supabase_service_role_key="fake-key",
        )
        assert s.auth0_domain == "example.auth0.com"

    def test_normalize_auth0_domain_strips_trailing_slash(self):
        s = Settings(
            auth0_domain="example.auth0.com/",
            supabase_url="https://fake.supabase.co",
            supabase_service_role_key="fake-key",
        )
        assert s.auth0_domain == "example.auth0.com"

    def test_normalize_auth0_domain_plain(self):
        s = Settings(
            auth0_domain="example.auth0.com",
            supabase_url="https://fake.supabase.co",
            supabase_service_role_key="fake-key",
        )
        assert s.auth0_domain == "example.auth0.com"

    def test_admin_emails_parsed(self):
        s = Settings(
            auth0_domain="test.auth0.com",
            supabase_url="https://fake.supabase.co",
            supabase_service_role_key="fake-key",
            admin_emails="a@test.com, b@test.com",
        )
        assert s.admin_emails == "a@test.com, b@test.com"


class TestProductionValidation:
    @patch.dict("os.environ", {"ENVIRONMENT": "production"})
    def test_raises_on_missing_config_in_production(self):
        with pytest.raises(ValueError, match="Missing required config"):
            Settings(
                auth0_domain="",
                auth0_api_audience="",
                supabase_url="",
                supabase_service_role_key="",
            )

    @patch.dict("os.environ", {"ENVIRONMENT": "development"})
    def test_allows_empty_config_in_development(self):
        s = Settings(
            auth0_domain="",
            auth0_api_audience="",
            supabase_url="",
            supabase_service_role_key="",
        )  # should not raise
        assert s.auth0_domain == ""
