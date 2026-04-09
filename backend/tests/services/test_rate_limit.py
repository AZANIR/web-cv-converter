from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest
from fastapi import HTTPException

from services.rate_limit import check_and_record_conversion


def _fake_settings(limit: int = 3):
    class S:
        conversions_per_hour = limit
    return S()


@patch("services.rate_limit.get_settings")
def test_allows_up_to_limit(mock_get):
    mock_get.return_value = _fake_settings(limit=3)
    sb = MagicMock()
    sb.table().select().eq().gte().execute.return_value = MagicMock(count=2)
    check_and_record_conversion("user-1", sb)


@patch("services.rate_limit.get_settings")
def test_raises_429_on_exceeding_limit(mock_get):
    mock_get.return_value = _fake_settings(limit=2)
    sb = MagicMock()
    sb.table().select().eq().gte().execute.return_value = MagicMock(count=3)
    with pytest.raises(HTTPException) as exc:
        check_and_record_conversion("user-1", sb)
    assert exc.value.status_code == 429


@patch("services.rate_limit.get_settings")
def test_under_limit_succeeds(mock_get):
    mock_get.return_value = _fake_settings(limit=5)
    sb = MagicMock()
    sb.table().select().eq().gte().execute.return_value = MagicMock(count=3)
    check_and_record_conversion("user-1", sb)
