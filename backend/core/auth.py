import asyncio

import jwt
from jwt import PyJWKClient
from fastapi import Depends, Header, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import get_settings
from .supabase import get_supabase

security = HTTPBearer(auto_error=False)

_jwk_clients: dict[str, PyJWKClient] = {}


def _get_jwk_client(domain: str) -> PyJWKClient:
    if domain not in _jwk_clients:
        url = f"https://{domain}/.well-known/jwks.json"
        _jwk_clients[domain] = PyJWKClient(url, cache_keys=True)
    return _jwk_clients[domain]


def _get_signing_key(token: str, domain: str):
    client = _get_jwk_client(domain)
    try:
        return client.get_signing_key_from_jwt(token)
    except Exception:
        return None


def _token_email(payload: dict) -> str | None:
    if payload.get("email"):
        return str(payload["email"])
    for key in payload:
        if key.endswith("/email") and isinstance(payload[key], str):
            return payload[key]
    return None


def _token_name_picture(payload: dict) -> tuple[str | None, str | None]:
    name = payload.get("name")
    picture = payload.get("picture")
    if not name:
        for k, v in payload.items():
            if k.endswith("/name") and isinstance(v, str):
                name = v
            if k.endswith("/picture") and isinstance(v, str):
                picture = v
    return name, picture


async def decode_auth0_token(token: str) -> dict:
    s = get_settings()
    if not s.auth0_domain or not s.auth0_api_audience:
        raise HTTPException(status_code=500, detail="Auth0 not configured")

    key = _get_signing_key(token, s.auth0_domain)
    if not key:
        raise HTTPException(status_code=401, detail="Invalid token key")

    try:
        payload = jwt.decode(
            token,
            key.key,
            algorithms=["RS256"],
            audience=s.auth0_api_audience,
            issuer=f"https://{s.auth0_domain}/",
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload


async def check_allowed_email(email: str | None) -> None:
    if not email:
        raise HTTPException(
            status_code=403,
            detail=(
                "Email missing from access token. Send header X-Auth0-ID-Token (set AUTH0_CLIENT_ID on "
                "the API), or add an email claim to the access token via an Auth0 Action."
            ),
        )
    sb = get_supabase()
    result = await asyncio.to_thread(
        lambda: sb.table("allowed_emails").select("email").eq("email", email).limit(1).execute()
    )
    if not result.data:
        raise HTTPException(status_code=403, detail="Access not allowed")


async def upsert_profile(user_id: str, email: str | None, name: str | None, avatar_url: str | None) -> None:
    if not email:
        return
    sb = get_supabase()
    existing = await asyncio.to_thread(
        lambda: sb.table("profiles")
        .select("id,email,full_name,avatar_url")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )
    if existing.data:
        row = existing.data[0]
        if (
            row.get("email") == email
            and row.get("full_name") == name
            and row.get("avatar_url") == avatar_url
        ):
            return
        await asyncio.to_thread(
            lambda: sb.table("profiles").update(
                {
                    "email": email,
                    "full_name": name,
                    "avatar_url": avatar_url,
                }
            ).eq("id", user_id).execute()
        )
    else:
        await asyncio.to_thread(
            lambda: sb.table("profiles").insert(
                {
                    "id": user_id,
                    "email": email,
                    "full_name": name,
                    "avatar_url": avatar_url,
                }
            ).execute()
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
    id_token_header: str | None = Header(None, alias="X-Auth0-ID-Token"),
) -> dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = await decode_auth0_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    email = _token_email(payload)
    name, picture = _token_name_picture(payload)

    if not email and id_token_header:
        s = get_settings()
        if s.auth0_client_id:
            id_key = _get_signing_key(id_token_header, s.auth0_domain)
            if not id_key:
                raise HTTPException(status_code=401, detail="Invalid id token")
            try:
                id_payload = jwt.decode(
                    id_token_header,
                    id_key.key,
                    algorithms=["RS256"],
                    audience=s.auth0_client_id,
                    issuer=f"https://{s.auth0_domain}/",
                )
            except jwt.PyJWTError:
                raise HTTPException(status_code=401, detail="Invalid id token")
            if id_payload.get("sub") != user_id:
                raise HTTPException(status_code=401, detail="Token subject mismatch")
            email = _token_email(id_payload)
            if not name and not picture:
                name, picture = _token_name_picture(id_payload)

    await check_allowed_email(email)
    await upsert_profile(user_id, email, name, picture)

    return {"user_id": user_id, "email": email}


def is_config_listed_admin(email: str | None) -> bool:
    if not email:
        return False
    s = get_settings()
    allowed = {x.strip().lower() for x in s.admin_emails.split(",") if x.strip()}
    return email.strip().lower() in allowed


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if is_config_listed_admin(user.get("email")):
        return user
    sb = get_supabase()
    result = await asyncio.to_thread(
        lambda: sb.table("profiles").select("role").eq("id", user["user_id"]).limit(1).execute()
    )
    row = result.data[0] if result.data else None
    if row and row.get("role") == "admin":
        return user
    raise HTTPException(status_code=403, detail="Admin access required")
