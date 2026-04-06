from __future__ import annotations

import time
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from services.rate_limit import _window, check_and_record_conversion


@pytest.fixture(autouse=True)
def _clear_window():
    _window.clear()
    yield
    _window.clear()


def _fake_settings(limit: int = 3):
    class S:
        conversions_per_hour = limit
    return S()


@patch("services.rate_limit.get_settings")
def test_allows_up_to_limit(mock_get):
    mock_get.return_value = _fake_settings(limit=3)
    for _ in range(3):
        check_and_record_conversion("user-1")


@patch("services.rate_limit.get_settings")
def test_raises_429_on_exceeding_limit(mock_get):
    mock_get.return_value = _fake_settings(limit=2)
    check_and_record_conversion("user-1")
    check_and_record_conversion("user-1")
    with pytest.raises(HTTPException) as exc:
        check_and_record_conversion("user-1")
    assert exc.value.status_code == 429


@patch("services.rate_limit.get_settings")
def test_different_users_have_separate_windows(mock_get):
    mock_get.return_value = _fake_settings(limit=1)
    check_and_record_conversion("user-a")
    check_and_record_conversion("user-b")


@patch("services.rate_limit.get_settings")
def test_expired_entries_are_evicted(mock_get):
    mock_get.return_value = _fake_settings(limit=1)
    check_and_record_conversion("user-1")
    _window["user-1"] = [time.time() - 7200]
    check_and_record_conversion("user-1")
