import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.config import get_settings
from core.supabase import get_supabase
from routers import admin, convert, generate, generate_history, history, me, prompts
from services.conversion_runner import recover_pending_conversions
from services.generation_runner import recover_pending_generations


def configure_logging() -> None:
    """Attach handlers to the root logger (console always; file if writable).

    File logging can fail on read-only images or missing volume permissions; in
    that case stderr still receives all application logs (visible in ``docker logs``).
    """
    s = get_settings()
    log_level_name = (s.log_level or "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    log_path = Path(s.log_file_path)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=s.log_max_bytes,
            backupCount=s.log_backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except OSError as e:
        sys.stderr.write(
            f"[logging] Could not open log file {log_path!r} ({e}); "
            "using stderr only (check docker logs).\n"
        )

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True
        logger.setLevel(log_level)


configure_logging()

_app_logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Re-apply after uvicorn's dictConfig (defensive) so app + task loggers stay wired.
    configure_logging()
    _app_logger.info("Logging configured (level=%s)", (get_settings().log_level or "INFO").upper())
    await recover_pending_conversions()
    await recover_pending_generations()
    yield


_is_production = os.getenv("ENVIRONMENT", "").lower() == "production"

app = FastAPI(
    title="CV Converter API",
    lifespan=lifespan,
    docs_url=None if _is_production else "/docs",
    redoc_url=None if _is_production else "/redoc",
    openapi_url=None if _is_production else "/openapi.json",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


_settings = get_settings()
_origins = [o.strip() for o in _settings.allowed_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Auth0-ID-Token"],
)
app.add_middleware(SecurityHeadersMiddleware)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/health/full")
async def health_full():
    try:
        sb = get_supabase()
        await asyncio.to_thread(lambda: sb.table("profiles").select("id").limit(1).execute())
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {"status": "ok", "db": db_status}


app.include_router(me.router, prefix="/api")
app.include_router(convert.router, prefix="/api")
app.include_router(generate_history.router, prefix="/api")
app.include_router(generate.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(prompts.router, prefix="/api")
