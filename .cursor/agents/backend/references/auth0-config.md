# Auth0 Configuration

## How Auth Works in this Project

1. Frontend authenticates via Auth0 OAuth2 flow using `nuxt-auth-utils`
2. Frontend stores session server-side (not in localStorage)
3. Frontend server routes proxy calls to FastAPI with Bearer token
4. FastAPI validates JWT RS256 via Auth0 JWKS endpoint in `core/auth.py`
5. Email verified against `allowed_emails` Supabase table
6. User profile upserted to `profiles` table on each valid request

## Key Functions in `core/auth.py`

| Function | Purpose |
|---|---|
| `get_current_user(credentials, id_token_header)` | FastAPI dependency — validates JWT, checks email allowlist, upserts profile. Returns `{"user_id": str, "email": str}` |
| `require_admin(user)` | FastAPI dependency — wraps `get_current_user`, checks `admin_emails` config or `profiles.role = "admin"` |
| `decode_auth0_token(token)` | Internal — validates RS256 JWT against Auth0 JWKS |
| `check_allowed_email(email)` | Internal — checks `allowed_emails` table |

## Required Environment Variables

| Variable | Description |
|---|---|
| `AUTH0_DOMAIN` | Auth0 domain (e.g. `dev-xxx.us.auth0.com`) |
| `AUTH0_API_AUDIENCE` | API audience identifier |
| `AUTH0_CLIENT_ID` | SPA client ID (optional, for ID token email fallback) |
| `ADMIN_EMAILS` | Comma-separated admin email list |

## Adding New Auth0 Settings

If a new Auth0 setting is needed, add it to `Settings` in `core/config.py`:

```python
class Settings(BaseSettings):
    # ... existing ...
    auth0_new_setting: str = ""
```

Then read it via `get_settings().auth0_new_setting`.

## Auth Dependency Usage

```python
# Standard protected endpoint
@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    return user  # {"user_id": "auth0|...", "email": "user@example.com"}

# Admin-only endpoint
@router.delete("/{id}")
async def delete_item(id: str, user: dict = Depends(require_admin)):
    ...
```

## X-Auth0-ID-Token Header

When the Auth0 API access token does not contain an email claim, the frontend can send the ID token in the `X-Auth0-ID-Token` header. `get_current_user` will decode it to extract the email. This is already handled in `core/auth.py`.
