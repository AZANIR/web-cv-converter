from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import jwt as pyjwt
import pytest
from fastapi import HTTPException

from core.auth import (
    _token_email,
    _token_name_picture,
    is_config_listed_admin,
    check_allowed_email,
    decode_auth0_token,
)


class TestTokenEmail:
    def test_returns_direct_email(self):
        assert _token_email({"email": "user@test.com"}) == "user@test.com"

    def test_returns_namespaced_email(self):
        payload = {"https://myapp.com/email": "ns@test.com"}
        assert _token_email(payload) == "ns@test.com"

    def test_returns_none_when_no_email(self):
        assert _token_email({"sub": "auth0|123"}) is None

    def test_coerces_non_string_email_to_string(self):
        assert _token_email({"email": 123}) == "123"

    def test_prefers_direct_email(self):
        payload = {
            "email": "direct@test.com",
            "https://app.com/email": "ns@test.com",
        }
        assert _token_email(payload) == "direct@test.com"


class TestTokenNamePicture:
    def test_returns_direct_name_and_picture(self):
        payload = {"name": "Alice", "picture": "https://pic.url"}
        name, picture = _token_name_picture(payload)
        assert name == "Alice"
        assert picture == "https://pic.url"

    def test_returns_namespaced_name(self):
        payload = {"https://app.com/name": "Bob", "https://app.com/picture": "https://pic2.url"}
        name, picture = _token_name_picture(payload)
        assert name == "Bob"
        assert picture == "https://pic2.url"

    def test_returns_none_when_missing(self):
        name, picture = _token_name_picture({"sub": "auth0|123"})
        assert name is None
        assert picture is None


class TestIsConfigListedAdmin:
    @patch("core.auth.get_settings")
    def test_returns_true_for_listed_email(self, mock_settings):
        mock_settings.return_value = MagicMock(admin_emails="admin@test.com, super@test.com")
        assert is_config_listed_admin("admin@test.com") is True

    @patch("core.auth.get_settings")
    def test_case_insensitive(self, mock_settings):
        mock_settings.return_value = MagicMock(admin_emails="Admin@Test.com")
        assert is_config_listed_admin("admin@test.com") is True

    @patch("core.auth.get_settings")
    def test_returns_false_for_unlisted_email(self, mock_settings):
        mock_settings.return_value = MagicMock(admin_emails="admin@test.com")
        assert is_config_listed_admin("user@test.com") is False

    def test_returns_false_for_none(self):
        assert is_config_listed_admin(None) is False

    @patch("core.auth.get_settings")
    def test_handles_empty_admin_list(self, mock_settings):
        mock_settings.return_value = MagicMock(admin_emails="")
        assert is_config_listed_admin("admin@test.com") is False


class TestCheckAllowedEmail:
    @patch("core.auth.get_supabase")
    async def test_raises_403_when_no_email(self, mock_sb):
        with pytest.raises(HTTPException) as exc:
            await check_allowed_email(None)
        assert exc.value.status_code == 403

    @patch("core.auth.get_supabase")
    async def test_raises_403_when_email_not_in_whitelist(self, mock_sb):
        sb = MagicMock()
        sb.table.return_value = sb
        sb.select.return_value = sb
        sb.eq.return_value = sb
        sb.limit.return_value = sb
        sb.execute.return_value = MagicMock(data=[])
        mock_sb.return_value = sb

        with pytest.raises(HTTPException) as exc:
            await check_allowed_email("unknown@test.com")
        assert exc.value.status_code == 403

    @patch("core.auth.get_supabase")
    async def test_passes_when_email_in_whitelist(self, mock_sb):
        sb = MagicMock()
        sb.table.return_value = sb
        sb.select.return_value = sb
        sb.eq.return_value = sb
        sb.limit.return_value = sb
        sb.execute.return_value = MagicMock(data=[{"email": "user@test.com"}])
        mock_sb.return_value = sb

        await check_allowed_email("user@test.com")


class TestDecodeAuth0Token:
    @patch("core.auth.get_settings")
    async def test_raises_500_when_not_configured(self, mock_settings):
        mock_settings.return_value = MagicMock(auth0_domain="", auth0_api_audience="")
        with pytest.raises(HTTPException) as exc:
            await decode_auth0_token("some-token")
        assert exc.value.status_code == 500

    @patch("core.auth._get_signing_key")
    @patch("core.auth.get_settings")
    async def test_raises_401_when_no_signing_key(self, mock_settings, mock_get_key):
        mock_settings.return_value = MagicMock(
            auth0_domain="test.auth0.com",
            auth0_api_audience="https://api",
        )
        mock_get_key.return_value = None
        with pytest.raises(HTTPException) as exc:
            await decode_auth0_token("some-token")
        assert exc.value.status_code == 401



class TestJWTAlgorithmRestriction:
    """Verify that decode_auth0_token rejects algorithm confusion attacks (CVE-2024-33663/33664)."""

    @patch("core.auth._get_signing_key")
    @patch("core.auth.get_settings")
    async def test_rejects_alg_none(self, mock_settings, mock_get_key):
        """Tokens with alg=none must be rejected."""
        mock_settings.return_value = MagicMock(
            auth0_domain="test.auth0.com",
            auth0_api_audience="https://api",
        )
        # Craft a token with alg: none (unsigned)
        header = json.dumps({"alg": "none", "typ": "JWT"})
        import base64
        h_b64 = base64.urlsafe_b64encode(header.encode()).rstrip(b"=").decode()
        payload = json.dumps({"sub": "auth0|123", "aud": "https://api", "iss": "https://test.auth0.com/"})
        p_b64 = base64.urlsafe_b64encode(payload.encode()).rstrip(b"=").decode()
        none_token = f"{h_b64}.{p_b64}."

        # _get_signing_key will fail on a none-alg token (no kid), returning None
        mock_get_key.return_value = None

        with pytest.raises(HTTPException) as exc:
            await decode_auth0_token(none_token)
        assert exc.value.status_code == 401

    @patch("core.auth._get_signing_key")
    @patch("core.auth.get_settings")
    async def test_rejects_hs256_token(self, mock_settings, mock_get_key):
        """HS256 tokens must be rejected because decode only allows RS256."""
        hmac_secret = "super-secret-key"

        mock_settings.return_value = MagicMock(
            auth0_domain="test.auth0.com",
            auth0_api_audience="https://api",
        )

        # Create a valid HS256 token
        hs256_token = pyjwt.encode(
            {"sub": "auth0|123", "aud": "https://api", "iss": "https://test.auth0.com/"},
            hmac_secret,
            algorithm="HS256",
        )

        # Simulate _get_signing_key returning a mock key whose .key is the HMAC secret
        mock_key = MagicMock()
        mock_key.key = hmac_secret
        mock_get_key.return_value = mock_key

        # PyJWT with algorithms=["RS256"] must reject the HS256 token
        with pytest.raises(HTTPException) as exc:
            await decode_auth0_token(hs256_token)
        assert exc.value.status_code == 401
