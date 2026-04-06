from functools import lru_cache
import re

from supabase import Client, create_client
import supabase._sync.client as _sc

from .config import get_settings

# supabase-py 2.28 still validates the key as JWT even though Supabase
# Dashboard now issues sb_secret_ keys.  Patch the regex to also accept them.
_ORIG_RE = r"^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$"
_PATCHED_RE = r"^(sb_secret_[A-Za-z0-9_-]+|[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*)$"
_sc.re.match = (lambda _orig: lambda pattern, string, *a, **kw: _orig(_PATCHED_RE if pattern == _ORIG_RE else pattern, string, *a, **kw))(re.match)


@lru_cache
def get_supabase() -> Client:
    s = get_settings()
    return create_client(s.supabase_url, s.supabase_service_role_key)
