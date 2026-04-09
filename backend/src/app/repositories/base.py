"""Reusable repository primitives for SQLAlchemy-backed persistence."""

from __future__ import annotations

import uuid
from typing import TypeVar

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class SQLAlchemyRepository[ModelT]:
    """Thin typed wrapper around common SQLAlchemy persistence operations."""

    model_type: type[ModelT]

    def __init__(self, session: Session) -> None:
        """Bind the repository instance to a live SQLAlchemy session."""

        self.session = session

    def get(self, entity_id: uuid.UUID) -> ModelT | None:
        """Return one entity by identifier or ``None`` when missing."""

        return self.session.get(self.model_type, entity_id)

    def add(self, instance: ModelT) -> ModelT:
        """Attach an entity to the session and return it for chaining."""

        self.session.add(instance)
        return instance

    def list(self, limit: int = 100, offset: int = 0) -> list[ModelT]:
        """Return a paginated collection of entities for the repository model."""

        statement = self.base_query().limit(limit).offset(offset)
        return list(self.session.scalars(statement))

    def base_query(self) -> Select[tuple[ModelT]]:
        """Build the repository's default select statement."""

        return select(self.model_type)
