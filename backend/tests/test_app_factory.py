"""Tests for FastAPI application bootstrap behavior."""

from app.main import create_app
from fastapi import FastAPI


def test_create_app_returns_fastapi_instance() -> None:
    """The application factory should always build a FastAPI app."""

    app = create_app()

    assert isinstance(app, FastAPI)


def test_root_endpoint_returns_service_metadata(client) -> None:
    """The root endpoint should expose minimal service metadata."""

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
