from __future__ import annotations

import importlib
import sys
import types
from unittest.mock import patch

import pytest


def test_configure_logging_rotating_handler_oserror_uses_stderr(tmp_path, capsys):
    from core.config import Settings

    # `backend/main.py` imports slowapi at module import time, but this unit test
    # is only about logging. If `slowapi` is not installed in the test env,
    # provide a minimal stub so `import main` can succeed.
    if "slowapi" not in sys.modules:
        slowapi = types.ModuleType("slowapi")

        class Limiter:  # type: ignore[no-redef]
            def __init__(self, *args, **kwargs) -> None:
                pass

        slowapi.Limiter = Limiter
        slowapi._rate_limit_exceeded_handler = lambda *args, **kwargs: None  # type: ignore[assignment]

        errors = types.ModuleType("slowapi.errors")

        class RateLimitExceeded(Exception):
            pass

        errors.RateLimitExceeded = RateLimitExceeded

        util = types.ModuleType("slowapi.util")
        util.get_remote_address = lambda request: "127.0.0.1"  # type: ignore[assignment]

        sys.modules["slowapi"] = slowapi
        sys.modules["slowapi.errors"] = errors
        sys.modules["slowapi.util"] = util

    # Import inside the test after stubbing.
    if "main" in sys.modules:
        importlib.reload(sys.modules["main"])
    else:
        importlib.import_module("main")

    import main

    s = Settings(log_file_path=str(tmp_path / "backend.log"), log_level="INFO")

    with (
        patch.dict("os.environ", {"ENVIRONMENT": "development"}),
        patch("main.get_settings", return_value=s),
        patch("main.RotatingFileHandler", side_effect=OSError("no perms")),
    ):
        main.configure_logging()

    captured = capsys.readouterr()
    assert "Could not open log file" in captured.err

