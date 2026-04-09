"""Memory service scaffolding shared by future versioned workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from datetime import datetime
import uuid

from app.core.enums import MemoryVersionStatus
from app.core.exceptions import ConflictError, NotFoundError
from app.models.memory import MemoryItem, MemoryVersion
from app.schemas.memory import MemoryItemCreate, MemoryVersionCreate


class MemorySessionProtocol(Protocol):
    """Protocol describing the session methods used by the memory service."""

    def add(self, instance: object) -> None:
        """Track an instance for persistence."""

    def commit(self) -> None:
        """Persist the current transaction."""

    def refresh(self, instance: object) -> None:
        """Refresh an instance from the underlying store."""


class MemoryItemRepositoryProtocol(Protocol):
    """Protocol describing the item repository behavior the service relies on."""

    session: MemorySessionProtocol

    def get(self, entity_id: uuid.UUID) -> MemoryItem | None:
        """Return a memory item by id."""

    def add(self, instance: MemoryItem) -> MemoryItem:
        """Persist a memory item."""

    def list_for_influencer(self, influencer_id: uuid.UUID) -> list[MemoryItem]:
        """Return all memory items for an influencer."""

    def get_by_key(
        self,
        influencer_id: uuid.UUID,
        memory_type: str,
        key: str,
    ) -> MemoryItem | None:
        """Return one item by influencer-scoped logical key."""


class MemoryVersionRepositoryProtocol(Protocol):
    """Protocol describing the version repository behavior the service relies on."""

    session: MemorySessionProtocol

    def get(self, entity_id: uuid.UUID) -> MemoryVersion | None:
        """Return a memory version by id."""

    def add(self, instance: MemoryVersion) -> MemoryVersion:
        """Persist a memory version."""

    def list_for_item(self, memory_item_id: uuid.UUID) -> list[MemoryVersion]:
        """Return all versions for a memory item."""

    def get_for_item(
        self,
        memory_item_id: uuid.UUID,
        version_id: uuid.UUID,
    ) -> MemoryVersion | None:
        """Return a version only when it belongs to the specified item."""


@dataclass(slots=True)
class MemoryItemDetail:
    """Detailed memory view combining the logical item and its versions."""

    item: MemoryItem
    versions: list[MemoryVersion]


@dataclass(slots=True)
class PublishMemoryVersionResult:
    """Result returned after publishing a memory version."""

    item: MemoryItem
    version: MemoryVersion


class MemoryService:
    """Coordinate versioned memory retrieval rules for influencers."""

    def __init__(
        self,
        memory_items: MemoryItemRepositoryProtocol,
        memory_versions: MemoryVersionRepositoryProtocol,
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

    def get_memory_detail(self, memory_item_id: uuid.UUID) -> MemoryItemDetail:
        """Return a memory item together with all of its versions."""

        item = self.get_memory_item_or_raise(memory_item_id)
        versions = self.memory_versions.list_for_item(memory_item_id)
        return MemoryItemDetail(item=item, versions=versions)

    def create_memory_item(self, payload: MemoryItemCreate) -> MemoryItemDetail:
        """Create a logical memory item and its first immutable version."""

        if self.memory_items.get_by_key(
            influencer_id=payload.influencer_id,
            memory_type=payload.memory_type.value,
            key=payload.key,
        ) is not None:
            raise ConflictError(
                message="A memory item with this key already exists for the influencer.",
                details={
                    "influencer_id": str(payload.influencer_id),
                    "memory_type": payload.memory_type.value,
                    "key": payload.key,
                },
            )

        item = MemoryItem(
            id=uuid.uuid4(),
            influencer_id=payload.influencer_id,
            memory_type=payload.memory_type.value,
            subtype=payload.subtype,
            key=payload.key,
            title=payload.title,
            is_invariant=payload.is_invariant,
            is_mutable=payload.is_mutable,
        )
        self.memory_items.add(item)

        version = self._build_version(
            memory_item_id=item.id,
            payload=payload.initial_version,
            version_number=1,
        )
        self.memory_versions.add(version)

        if payload.initial_version.publish:
            item.current_version_id = version.id
            version.status = MemoryVersionStatus.PUBLISHED.value

        self.memory_items.session.add(item)
        self.memory_items.session.commit()
        self.memory_items.session.refresh(item)
        self.memory_versions.session.refresh(version)
        return MemoryItemDetail(item=item, versions=[version])

    def create_memory_version(
        self,
        memory_item_id: uuid.UUID,
        payload: MemoryVersionCreate,
    ) -> MemoryVersion:
        """Create a new immutable version for an existing memory item."""

        item = self.get_memory_item_or_raise(memory_item_id)
        existing_versions = self.memory_versions.list_for_item(memory_item_id)
        next_version = (existing_versions[0].version + 1) if existing_versions else 1

        version = self._build_version(
            memory_item_id=item.id,
            payload=payload,
            version_number=next_version,
        )
        if payload.publish:
            self._archive_published_versions(existing_versions)
            version.status = MemoryVersionStatus.PUBLISHED.value
            item.current_version_id = version.id

        self.memory_versions.add(version)
        self.memory_items.session.add(item)
        self.memory_items.session.commit()
        self.memory_versions.session.refresh(version)
        self.memory_items.session.refresh(item)
        return version

    def publish_memory_version(
        self,
        memory_item_id: uuid.UUID,
        version_id: uuid.UUID,
    ) -> PublishMemoryVersionResult:
        """Publish one memory version and update the item's active pointer."""

        item = self.get_memory_item_or_raise(memory_item_id)
        version = self.memory_versions.get_for_item(memory_item_id, version_id)
        if version is None:
            raise NotFoundError(
                "Memory version",
                {"memory_item_id": str(memory_item_id), "version_id": str(version_id)},
            )

        versions = self.memory_versions.list_for_item(memory_item_id)
        self._archive_published_versions(versions, keep_version_id=version.id)
        version.status = MemoryVersionStatus.PUBLISHED.value
        item.current_version_id = version.id

        self.memory_versions.session.add(version)
        self.memory_items.session.add(item)
        self.memory_items.session.commit()
        self.memory_versions.session.refresh(version)
        self.memory_items.session.refresh(item)
        return PublishMemoryVersionResult(item=item, version=version)

    def _build_version(
        self,
        memory_item_id: uuid.UUID,
        payload: MemoryVersionCreate,
        version_number: int,
    ) -> MemoryVersion:
        """Construct a memory version model from the incoming schema payload."""

        return MemoryVersion(
            id=uuid.uuid4(),
            memory_item_id=memory_item_id,
            version=version_number,
            status=(
                MemoryVersionStatus.PUBLISHED.value
                if payload.publish
                else MemoryVersionStatus.DRAFT.value
            ),
            payload=payload.payload,
            summary=payload.summary,
            change_reason=payload.change_reason,
            source=payload.source,
            created_by=payload.created_by,
            effective_at=payload.effective_at,
            expires_at=payload.expires_at,
        )

    def _archive_published_versions(
        self,
        versions: list[MemoryVersion],
        keep_version_id: uuid.UUID | None = None,
    ) -> None:
        """Archive previously published versions before a new one becomes active."""

        for version in versions:
            if version.status != MemoryVersionStatus.PUBLISHED.value:
                continue
            if keep_version_id is not None and version.id == keep_version_id:
                continue
            version.status = MemoryVersionStatus.ARCHIVED.value
            self.memory_versions.session.add(version)
