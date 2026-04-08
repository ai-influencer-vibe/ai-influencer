"""Memory service scaffolding shared by future versioned workflows."""

from __future__ import annotations

import uuid

from app.core.exceptions import NotFoundError
from app.models.memory import MemoryItem
from app.repositories.memory import MemoryItemRepository, MemoryVersionRepository


class MemoryService:
    """Coordinate versioned memory retrieval rules for influencers."""

    def __init__(
        self,
        memory_items: MemoryItemRepository,
        memory_versions: MemoryVersionRepository,
    ) -> None:
        """Bind the service to its underlying persistence dependencies."""

        self.memory_items = memory_items
        self.memory_versions = memory_versions

    def get_memory_item_or_raise(self, memory_item_id: uuid.UUID) -> MemoryItem:
        """Return one memory item or raise a typed not-found error."""

        memory_item = self.memory_items.get(memory_item_id)
        if memory_item is None:
            raise NotFoundError("Memory item", {"memory_item_id": str(memory_item_id)})
        return memory_item

    def list_influencer_memory(self, influencer_id: uuid.UUID) -> list[MemoryItem]:
        """Return the logical memory records attached to an influencer."""

        return self.memory_items.list_for_influencer(influencer_id)
