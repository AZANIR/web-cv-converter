# pytest Patterns

## Overriding Auth Dependency in Tests

```python
# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from main import app
from core.auth import get_current_user

MOCK_USER = {"user_id": "test-user-123", "email": "test@example.com"}

@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER
    yield TestClient(app)
    app.dependency_overrides.clear()
```

## Router Test Pattern

```python
# backend/tests/test_convert_router.py
from unittest.mock import patch, AsyncMock


def test_convert_success(client):
    with patch("routers.convert.ConversionService.run", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = {"id": "conv-1", "status": "done"}
        response = client.post("/api/convert", json={"markdown": "# Hello", "vacancy": "..."})
    assert response.status_code == 200
    assert response.json()["id"] == "conv-1"


def test_convert_unauthenticated():
    from fastapi.testclient import TestClient
    from main import app
    unauthenticated_client = TestClient(app)
    response = unauthenticated_client.post("/api/convert", json={"markdown": "# Hello"})
    assert response.status_code == 401


def test_convert_missing_body(client):
    response = client.post("/api/convert", json={})
    assert response.status_code == 422  # Pydantic validation error
```

## Service Test Pattern

```python
# backend/tests/test_{resource}_service.py
import pytest
from unittest.mock import MagicMock, patch
from services.{resource}_service import {Resource}Service


@pytest.fixture
def mock_supabase():
    with patch("services.{resource}_service.get_supabase") as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client


def test_create_success(mock_supabase):
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
        {"id": "row-1", "user_id": "user-1"}
    ]
    service = {Resource}Service()
    result = service.create("user-1", {"field": "value"})
    assert result["id"] == "row-1"


def test_get_not_found(mock_supabase):
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value.data = []
    service = {Resource}Service()
    result = service.get("nonexistent", "user-1")
    assert result is None
```

## Run Commands

```bash
# Run all tests
cd backend && pytest

# Run with coverage
cd backend && pytest --cov=. --cov-report=term-missing

# Run specific test file
cd backend && pytest tests/test_convert_router.py -v

# Run specific test
cd backend && pytest tests/test_convert_router.py::test_convert_success -v
```
