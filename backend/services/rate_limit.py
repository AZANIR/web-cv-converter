from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from supabase import Client

from core.config import get_settings


def check_and_record_conversion(user_id: str, sb: Client) -> None:
    s = get_settings()
    since = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

    res = sb.table("conversions") \
        .select("id", count="exact") \
        .eq("user_id", user_id) \
        .gte("created_at", since) \
        .execute()

    if (res.count or 0) >= s.conversions_per_hour:
        raise HTTPException(status_code=429, detail="Conversion rate limit exceeded")
