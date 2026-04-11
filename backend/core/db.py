"""Data access helpers that enforce tenant isolation."""

from supabase import Client

from .supabase import get_supabase


def user_table(table_name: str, user_id: str) -> Client:
    """Return a query builder pre-filtered to the given user.

    Usage: user_table("conversions", user_id).select("*").execute()
    This ensures every query is scoped to the user, preventing data leaks.
    """
    sb = get_supabase()
    return sb.table(table_name).eq("user_id", user_id)
