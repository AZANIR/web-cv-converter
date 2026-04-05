import time
from collections import defaultdict

from fastapi import HTTPException

from core.config import get_settings

_window: dict[str, list[float]] = defaultdict(list)


def check_and_record_conversion(user_id: str) -> None:
    s = get_settings()
    limit = s.conversions_per_hour
    now = time.time()
    window_start = now - 3600
    times = _window[user_id]
    times[:] = [t for t in times if t > window_start]
    if len(times) >= limit:
        raise HTTPException(status_code=429, detail="Conversion rate limit exceeded")
    times.append(now)
