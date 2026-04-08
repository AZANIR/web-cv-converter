# FastAPI Patterns

## Router Pattern

```python
# backend/routers/{resource}.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from core.auth import get_current_user
from services.{resource}_service import {Resource}Service

router = APIRouter(prefix="/{resource}s", tags=["{resource}"])


class {Resource}Request(BaseModel):
    field: str


class {Resource}Response(BaseModel):
    id: str
    field: str


@router.post("/", response_model={Resource}Response, status_code=201)
async def create_{resource}(
    body: {Resource}Request,
    user: dict = Depends(get_current_user),
) -> {Resource}Response:
    service = {Resource}Service()
    result = await service.create(user["user_id"], body)
    return result


@router.get("/{id}", response_model={Resource}Response)
async def get_{resource}(
    id: str,
    user: dict = Depends(get_current_user),
) -> {Resource}Response:
    service = {Resource}Service()
    result = await service.get(id, user["user_id"])
    if not result:
        raise HTTPException(status_code=404, detail="{Resource} not found")
    return result
```

## Service Pattern

```python
# backend/services/{resource}_service.py
from core.supabase import get_supabase


class {Resource}Service:
    def __init__(self):
        self.sb = get_supabase()
        self.table = "{resource}s"

    async def create(self, user_id: str, data: dict) -> dict:
        result = self.sb.table(self.table).insert({
            "user_id": user_id,
            **data,
        }).execute()
        return result.data[0]

    async def get(self, id: str, user_id: str) -> dict | None:
        result = (
            self.sb.table(self.table)
            .select("*")
            .eq("id", id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    async def list_for_user(self, user_id: str) -> list[dict]:
        result = (
            self.sb.table(self.table)
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data
```

## Register Router in main.py

```python
# backend/main.py — add to existing imports and registrations
from routers import {resource}
app.include_router({resource}.router, prefix="/api")
```

## Settings Pattern (adding new env var)

```python
# backend/core/config.py — add to Settings class
class Settings(BaseSettings):
    # ... existing fields ...
    new_service_api_key: str = ""
    new_service_base_url: str = "https://api.example.com"
```

## Error Handling Pattern

```python
from fastapi import HTTPException

# 400 — validation / bad request
raise HTTPException(status_code=400, detail="Invalid input: {reason}")

# 404 — not found
raise HTTPException(status_code=404, detail="{Resource} not found")

# 403 — forbidden (wrong owner)
raise HTTPException(status_code=403, detail="Access denied")

# 500 — unexpected (log first)
import logging
logger = logging.getLogger(__name__)
logger.exception("Unexpected error in {endpoint}")
raise HTTPException(status_code=500, detail="Internal server error")
```
