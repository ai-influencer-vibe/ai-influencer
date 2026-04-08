"""Repository access helpers for versioned memory records."""

from __future__ import annotations

import uuid

from sqlalchemy import Select, desc, select

from app.models.memory import MemoryItem, MemoryVersion
from app.repositories.base import SQLAlchemyRepository


class MemoryItemRepository(SQLAlchemyRepository[MemoryItem]):
    """Persistence operations for logical influencer memory items."""

    model_type = MemoryItem

    def list_for_influencer(self, influencer_id: uuid.UUID) -> list[MemoryItem]:
        """Return all memory items belonging to an influencer."""

        statement = (
            select(MemoryItem)
            .where(MemoryItem.influencer_id == influencer_id)
            .order_by(MemoryItem.memory_type.asc(), MemoryItem.key.asc())
        )
        return list(self.session.scalars(statement))


class MemoryVersionRepository(SQLAlchemyRepository[MemoryVersion]):
    """Persistence operations for immutable memory revisions."""

    model_type = MemoryVersion

    def list_for_item(self, memory_item_id: uuid.UUID) -> list[MemoryVersion]:
        """Return all versions for a memory item, newest first."""

        statement: Select[tuple[MemoryVersion]] = (
            select(MemoryVersion)
            .where(MemoryVersion.memory_item_id == memory_item_id)
            .order_by(desc(MemoryVersion.version))
        )
        return list(self.session.scalars(statement))
