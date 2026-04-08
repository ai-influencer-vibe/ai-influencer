"""Common response contracts reused across API endpoints."""

from pydantic import BaseModel, Field


class ErrorBody(BaseModel):
    """Serializable error payload used by application exception handlers."""

    code: str
    message: str
    details: dict[str, object] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Top-level error envelope returned by the API."""

    error: ErrorBody
