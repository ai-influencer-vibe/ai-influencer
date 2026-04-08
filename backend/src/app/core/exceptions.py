"""Shared domain exceptions used across services and APIs."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class AppError(Exception):
    """Base exception for predictable application-level failures."""

    message: str
    code: str
    status_code: int
    details: dict[str, object] = field(default_factory=dict)


class NotFoundError(AppError):
    """Raised when a requested domain entity does not exist."""

    def __init__(self, resource: str, details: dict[str, object] | None = None) -> None:
        super().__init__(
            message=f"{resource} was not found.",
            code="not_found",
            status_code=404,
            details=details or {"resource": resource},
        )


class ConflictError(AppError):
    """Raised when a write operation violates uniqueness or state rules."""

    def __init__(self, message: str, details: dict[str, object] | None = None) -> None:
        super().__init__(
            message=message,
            code="conflict",
            status_code=409,
            details=details or {},
        )


class DomainValidationError(AppError):
    """Raised when input passes transport validation but fails domain rules."""

    def __init__(self, message: str, details: dict[str, object] | None = None) -> None:
        super().__init__(
            message=message,
            code="domain_validation_error",
            status_code=422,
            details=details or {},
        )
