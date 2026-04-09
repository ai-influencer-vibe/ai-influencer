"""Tests for structured API error handling."""

from app.api.error_handlers import register_exception_handlers
from app.core.exceptions import ConflictError
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_app_errors_are_serialized_into_api_contract() -> None:
    """Custom domain exceptions should be returned as structured JSON."""

    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/conflict")
    async def conflict_route() -> None:
        raise ConflictError("Slug is already taken.", {"slug": "maya-rain"})

    client = TestClient(app)
    response = client.get("/conflict")

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "conflict",
            "message": "Slug is already taken.",
            "details": {"slug": "maya-rain"},
        }
    }
