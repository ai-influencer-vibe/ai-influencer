"""Unit tests for versioned memory workflows."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

import pytest
from app.core.enums import MemoryType, MemoryVersionStatus
from app.core.exceptions import ConflictError, NotFoundError
from app.models.memory import MemoryItem, MemoryVersion
from app.schemas.memory import MemoryItemCreate, MemoryVersionCreate
from app.services.memory_service import MemoryService


@dataclass
class FakeMemorySession:
    """Small fake session used to unit test versioned memory behavior."""

    committed: bool = False
    added: list[object] = field(default_factory=list)
    refreshed: list[object] = field(default_factory=list)

    def add(self, instance: object) -> None:
        """Record tracked objects for assertions."""

        self.added.append(instance)

    def commit(self) -> None:
        """Record that the service committed the transaction."""

        self.committed = True

    def refresh(self, instance: object) -> None:
        """Record refresh requests for assertions."""

        self.refreshed.append(instance)


class FakeMemoryItemRepository:
    """In-memory logical memory item repository for service tests."""

    def __init__(
        self,
        items: list[MemoryItem] | None = None,
        session: FakeMemorySession | None = None,
    ) -> None:
        self.items = items or []
        self.session = session or FakeMemorySession()

    def get(self, entity_id: uuid.UUID) -> MemoryItem | None:
        """Return one memory item by id."""

        return next((item for item in self.items if item.id == entity_id), None)

    def add(self, instance: MemoryItem) -> MemoryItem:
        """Persist a memory item in memory."""

        now = datetime.now(UTC)
        if instance.id is None:
            instance.id = uuid.uuid4()
        if instance.created_at is None:
            instance.created_at = now
        if instance.updated_at is None:
            instance.updated_at = now
        self.items.append(instance)
        self.session.add(instance)
        return instance

    def list_for_influencer(self, influencer_id: uuid.UUID) -> list[MemoryItem]:
        """Return all items belonging to one influencer."""

        return [item for item in self.items if item.influencer_id == influencer_id]

    def get_by_key(self, influencer_id: uuid.UUID, memory_type: str, key: str) -> MemoryItem | None:
        """Return one memory item by influencer-scoped logical key."""

        return next(
            (
                item
                for item in self.items
                if item.influencer_id == influencer_id
                and item.memory_type == memory_type
                and item.key == key
            ),
            None,
        )


class FakeMemoryVersionRepository:
    """In-memory immutable version repository for service tests."""

    def __init__(
        self,
        versions: list[MemoryVersion] | None = None,
        session: FakeMemorySession | None = None,
    ) -> None:
        self.versions = versions or []
        self.session = session or FakeMemorySession()

    def get(self, entity_id: uuid.UUID) -> MemoryVersion | None:
        """Return one memory version by id."""

        return next((version for version in self.versions if version.id == entity_id), None)

    def add(self, instance: MemoryVersion) -> MemoryVersion:
        """Persist a memory version in memory."""

        now = datetime.now(UTC)
        if instance.id is None:
            instance.id = uuid.uuid4()
        if instance.created_at is None:
            instance.created_at = now
        if instance.updated_at is None:
            instance.updated_at = now
        self.versions.append(instance)
        self.session.add(instance)
        return instance

    def list_for_item(self, memory_item_id: uuid.UUID) -> list[MemoryVersion]:
        """Return all versions for one memory item, newest first."""

        return sorted(
            [version for version in self.versions if version.memory_item_id == memory_item_id],
            key=lambda version: version.version,
            reverse=True,
        )

    def get_for_item(
        self,
        memory_item_id: uuid.UUID,
        version_id: uuid.UUID,
    ) -> MemoryVersion | None:
        """Return one version only when it belongs to the requested item."""

        return next(
            (
                version
                for version in self.versions
                if version.memory_item_id == memory_item_id and version.id == version_id
            ),
            None,
        )


def build_memory_item() -> MemoryItem:
    """Create a minimal memory item for unit tests."""

    now = datetime.now(UTC)
    return MemoryItem(
        id=uuid.uuid4(),
        influencer_id=uuid.uuid4(),
        memory_type=MemoryType.IDENTITY.value,
        key="identity-core",
        title="Identity Core",
        is_invariant=True,
        is_mutable=True,
        created_at=now,
        updated_at=now,
    )


def build_memory_version(
    memory_item_id: uuid.UUID,
    version: int,
    status: str = MemoryVersionStatus.DRAFT.value,
) -> MemoryVersion:
    """Create a minimal memory version for unit tests."""

    now = datetime.now(UTC)
    return MemoryVersion(
        id=uuid.uuid4(),
        memory_item_id=memory_item_id,
        version=version,
        status=status,
        payload={"name": "Maya Rain"},
        summary=f"Version {version}",
        source="operator",
        created_by="tester",
        effective_at=now,
        created_at=now,
        updated_at=now,
    )


def build_service(
    items: list[MemoryItem] | None = None,
    versions: list[MemoryVersion] | None = None,
) -> tuple[MemoryService, FakeMemoryItemRepository, FakeMemoryVersionRepository]:
    """Create a memory service backed by fake repositories."""

    session = FakeMemorySession()
    item_repo = FakeMemoryItemRepository(items=items, session=session)
    version_repo = FakeMemoryVersionRepository(versions=versions, session=session)
    return MemoryService(item_repo, version_repo), item_repo, version_repo


def test_create_memory_item_creates_initial_version() -> None:
    """Creating a memory item should also create version one."""

    service, item_repo, version_repo = build_service()
    influencer_id = uuid.uuid4()

    result = service.create_memory_item(
        MemoryItemCreate(
            influencer_id=influencer_id,
            memory_type=MemoryType.IDENTITY,
            key="identity-core",
            title="Identity Core",
            is_invariant=True,
            initial_version=MemoryVersionCreate(
                payload={"name": "Maya Rain"},
                summary="Initial identity",
                source="operator",
                created_by="architect",
                effective_at=datetime.now(UTC),
            ),
        )
    )

    assert result.item.influencer_id == influencer_id
    assert len(item_repo.items) == 1
    assert len(version_repo.versions) == 1
    assert result.versions[0].version == 1


def test_create_memory_item_rejects_duplicate_key() -> None:
    """Duplicate influencer-scoped memory keys should raise a conflict."""

    existing = build_memory_item()
    service, _, _ = build_service(items=[existing])

    with pytest.raises(ConflictError):
        service.create_memory_item(
            MemoryItemCreate(
                influencer_id=existing.influencer_id,
                memory_type=MemoryType.IDENTITY,
                key=existing.key,
                title="Duplicate",
                initial_version=MemoryVersionCreate(
                    payload={"name": "Maya Rain"},
                    summary="Duplicate identity",
                    source="operator",
                    created_by="architect",
                    effective_at=datetime.now(UTC),
                ),
            )
        )


def test_create_memory_version_increments_version_number() -> None:
    """New versions should increment from the latest stored revision."""

    item = build_memory_item()
    existing_version = build_memory_version(item.id, version=1)
    service, _, version_repo = build_service(items=[item], versions=[existing_version])

    result = service.create_memory_version(
        item.id,
        MemoryVersionCreate(
            payload={"name": "Maya Rain", "tone": "playful"},
            summary="Refined identity",
            source="operator",
            created_by="architect",
            effective_at=datetime.now(UTC),
        ),
    )

    assert result.version == 2
    assert len(version_repo.versions) == 2


def test_publish_memory_version_sets_current_pointer_and_archives_previous() -> None:
    """Publishing a version should update the current pointer and archive the old one."""

    item = build_memory_item()
    published = build_memory_version(item.id, version=1, status=MemoryVersionStatus.PUBLISHED.value)
    draft = build_memory_version(item.id, version=2, status=MemoryVersionStatus.DRAFT.value)
    item.current_version_id = published.id
    service, item_repo, version_repo = build_service(items=[item], versions=[published, draft])

    result = service.publish_memory_version(item.id, draft.id)

    assert result.item.current_version_id == draft.id
    assert draft.status == MemoryVersionStatus.PUBLISHED.value
    assert published.status == MemoryVersionStatus.ARCHIVED.value
    assert item_repo.session.committed is True
    assert version_repo.session.refreshed[-1] == draft


def test_publish_memory_version_raises_for_missing_version() -> None:
    """Publishing a missing version should raise a typed not-found error."""

    item = build_memory_item()
    service, _, _ = build_service(items=[item], versions=[])

    with pytest.raises(NotFoundError):
        service.publish_memory_version(item.id, uuid.uuid4())
