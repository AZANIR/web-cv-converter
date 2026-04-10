"""Tests for upsert_profile — verifies role is never overwritten on login."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from .conftest import make_supabase_mock


@pytest.fixture()
def sb():
    return make_supabase_mock()


@pytest.fixture(autouse=True)
def _patch_supabase(sb):
    with patch("core.auth.get_supabase", return_value=sb):
        yield


# ---------------------------------------------------------------------------
# upsert_profile
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_profile_skips_when_no_email(sb):
    from core.auth import upsert_profile

    await upsert_profile("uid1", None, "Alice", "https://img")

    sb.table.assert_not_called()


@pytest.mark.asyncio
async def test_upsert_profile_inserts_new_user(sb):
    """First login → insert row, do NOT touch role."""
    from core.auth import upsert_profile

    sb.execute.return_value = MagicMock(data=[])  # no existing profile

    await upsert_profile("uid-new", "new@test.com", "New User", "https://avatar")

    # select → insert path
    sb.insert.assert_called_once_with(
        {
            "id": "uid-new",
            "email": "new@test.com",
            "full_name": "New User",
            "avatar_url": "https://avatar",
        }
    )
    sb.update.assert_not_called()
    sb.upsert.assert_not_called()


@pytest.mark.asyncio
async def test_upsert_profile_updates_existing_user_without_role(sb):
    """Subsequent login → update only safe fields, role is NOT included."""
    from core.auth import upsert_profile

    # First execute() call (select) returns an existing profile row
    select_result = MagicMock(data=[{"id": "uid-existing"}])
    update_result = MagicMock(data=[])
    sb.execute.side_effect = [select_result, update_result]

    await upsert_profile("uid-existing", "admin@test.com", "Admin", "https://avatar")

    sb.update.assert_called_once_with(
        {
            "email": "admin@test.com",
            "full_name": "Admin",
            "avatar_url": "https://avatar",
        }
    )
    # Crucially: role must not appear in the update payload
    update_payload = sb.update.call_args[0][0]
    assert "role" not in update_payload

    sb.insert.assert_not_called()
    sb.upsert.assert_not_called()


@pytest.mark.asyncio
async def test_upsert_profile_role_preserved_across_login(sb):
    """Simulate an admin logging in twice — role must survive both calls."""
    from core.auth import upsert_profile

    existing = MagicMock(data=[{"id": "uid-admin"}])
    updated = MagicMock(data=[])
    sb.execute.side_effect = [existing, updated, existing, updated]

    await upsert_profile("uid-admin", "admin@test.com", "Admin", None)
    await upsert_profile("uid-admin", "admin@test.com", "Admin", None)

    assert sb.insert.call_count == 0
    assert sb.upsert.call_count == 0
    for call in sb.update.call_args_list:
        assert "role" not in call[0][0]
