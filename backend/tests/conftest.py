from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from core.auth import get_current_user, require_admin
from core.config import Settings, get_settings
from core.supabase import get_supabase


def _make_settings(**overrides) -> Settings:
    defaults = dict(
        auth0_domain="test.auth0.com",
        auth0_api_audience="https://test-api",
        auth0_client_id="test-client-id",
        supabase_url="https://fake.supabase.co",
        supabase_service_role_key="fake-key",
        ai_provider="gemini",
        gemini_api_key="fake-gemini-key",
        gemini_model="gemini-test",
        anthropic_api_key="fake-anthropic-key",
        allowed_origins="http://localhost:3000",
        admin_emails="admin@test.com",
        conversions_per_hour=10,
    )
    defaults.update(overrides)
    return Settings(**defaults)


class _ChainableMock(MagicMock):
    """Mock that supports Supabase's fluent .table().select().eq().execute() pattern."""

    def _get_child_mock(self, /, **kw):
        return _ChainableMock(**kw)


def make_supabase_mock() -> _ChainableMock:
    mock = _ChainableMock()
    mock.table.return_value = mock
    mock.select.return_value = mock
    mock.insert.return_value = mock
    mock.update.return_value = mock
    mock.upsert.return_value = mock
    mock.delete.return_value = mock
    mock.eq.return_value = mock
    mock.in_.return_value = mock
    mock.limit.return_value = mock
    mock.order.return_value = mock
    mock.execute.return_value = MagicMock(data=[])
    return mock


FAKE_USER = {"user_id": "auth0|user123", "email": "user@test.com"}
FAKE_ADMIN = {"user_id": "auth0|admin1", "email": "admin@test.com"}


@pytest.fixture()
def settings():
    return _make_settings()


@pytest.fixture()
def mock_supabase():
    return make_supabase_mock()


@pytest.fixture()
def app(settings, mock_supabase):
    """Provide a FastAPI app with dependency overrides and patched singletons."""
    get_settings.cache_clear()
    get_supabase.cache_clear()

    from main import app as _app

    _app.dependency_overrides[get_current_user] = lambda: FAKE_USER
    _app.dependency_overrides[require_admin] = lambda: FAKE_ADMIN

    with (
        patch("core.supabase.create_client", return_value=mock_supabase),
        patch("core.config.Settings", return_value=settings),
        patch("main.get_supabase", return_value=mock_supabase),
        patch("main.get_settings", return_value=settings),
        patch("routers.convert.get_supabase", return_value=mock_supabase),
        patch("routers.convert.get_settings", return_value=settings),
        patch("routers.history.get_supabase", return_value=mock_supabase),
        patch("routers.me.get_supabase", return_value=mock_supabase),
        patch("routers.admin.get_supabase", return_value=mock_supabase),
    ):
        yield _app

    _app.dependency_overrides.clear()
    get_settings.cache_clear()
    get_supabase.cache_clear()


@pytest.fixture()
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
