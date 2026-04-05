import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from core.supabase import get_supabase
from routers import admin, convert, history, me

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="CV Converter API")

_settings = get_settings()
_origins = [o.strip() for o in _settings.allowed_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    try:
        sb = get_supabase()
        sb.table("profiles").select("id").limit(1).execute()
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {"status": "ok", "db": db_status}


app.include_router(me.router, prefix="/api")
app.include_router(convert.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
