"""Shared FastAPI dependency providers."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db_session


def get_app_settings() -> Settings:
    """Return the cached application settings instance."""

    return get_settings()


def get_request_db_session() -> Generator[Session, None, None]:
    """Yield a database session for the lifetime of an HTTP request."""

    yield from get_db_session()
