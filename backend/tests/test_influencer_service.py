from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

import pytest

from app.core.enums import InfluencerStatus
from app.core.exceptions import ConflictError, NotFoundError
from app.models.influencer import Influencer
from app.schemas.influencer import InfluencerCreate, InfluencerUpdate
from app.services.influencer_service import InfluencerService


@dataclass
class FakeSession:
    """Small fake session used to unit test service behavior."""

    committed: bool = False
    refreshed: list[Influencer] = field(default_factory=list)
    added: list[Influencer] = field(default_factory=list)

    def add(self, instance: Influencer) -> None:
        """Record added instances for assertions."""

        self.added.append(instance)

    def commit(self) -> None:
        """Record that the service attempted to commit."""

        self.committed = True

    def refresh(self, instance: Influencer) -> None:
        """Record refresh requests for assertions."""

        self.refreshed.append(instance)


class FakeInfluencerRepository:
    """Fake repository mirroring the behavior the service relies on."""

    def __init__(self, items: list[Influencer] | None = None) -> None:
        self.items = items or []
        self.session = FakeSession()

    def get(self, entity_id: uuid.UUID) -> Influencer | None:
        """Return one influencer by id from the fake collection."""

        for item in self.items:
            if item.id == entity_id:
                return item
        return None

    def get_by_slug(self, slug: str) -> Influencer | None:
        """Return one influencer by slug from the fake collection."""

        for item in self.items:
            if item.slug == slug:
                return item
        return None

    def list(self, limit: int = 100, offset: int = 0) -> list[Influencer]:
        """Return a paginated slice from the fake collection."""

        return self.items[offset : offset + limit]

    def count(self) -> int:
        """Return the total number of fake influencers."""

        return len(self.items)

    def add(self, instance: Influencer) -> Influencer:
        """Persist an influencer in the fake collection."""

        if instance.id is None:
            instance.id = uuid.uuid4()
        now = datetime.now(UTC)
        if instance.created_at is None:
            instance.created_at = now
        if instance.updated_at is None:
            instance.updated_at = now
        self.items.append(instance)
        self.session.add(instance)
        return instance


def build_influencer(slug: str = "maya-rain") -> Influencer:
    """Create a minimal influencer model instance for unit tests."""

    now = datetime.now(UTC)
    return Influencer(
        id=uuid.uuid4(),
        slug=slug,
        display_name="Maya Rain",
        status=InfluencerStatus.DRAFT.value,
        default_language="en",
        primary_platform="instagram",
        created_at=now,
        updated_at=now,
    )


def test_create_influencer_persists_new_record() -> None:
    """Creating an influencer should enforce uniqueness and commit the write."""

    repository = FakeInfluencerRepository()
    service = InfluencerService(repository=repository)

    result = service.create_influencer(
        InfluencerCreate(
            slug="maya-rain",
            display_name="Maya Rain",
            description="Digital fashion creator",
            default_language="en",
            primary_platform="instagram",
        )
    )

    assert result.slug == "maya-rain"
    assert repository.session.committed is True
    assert repository.session.refreshed == [result]


def test_create_influencer_rejects_duplicate_slug() -> None:
    """Duplicate slugs should raise a typed conflict error."""

    repository = FakeInfluencerRepository(items=[build_influencer()])
    service = InfluencerService(repository=repository)

    with pytest.raises(ConflictError):
        service.create_influencer(
            InfluencerCreate(slug="maya-rain", display_name="Maya Rain")
        )


def test_get_or_raise_raises_not_found() -> None:
    """Missing influencer lookups should raise a typed not-found error."""

    repository = FakeInfluencerRepository()
    service = InfluencerService(repository=repository)

    with pytest.raises(NotFoundError):
        service.get_or_raise(uuid.uuid4())


def test_update_influencer_archives_and_sets_timestamp() -> None:
    """Archiving an influencer should set the archived timestamp."""

    influencer = build_influencer()
    repository = FakeInfluencerRepository(items=[influencer])
    service = InfluencerService(repository=repository)

    result = service.update_influencer(
        influencer.id,
        InfluencerUpdate(status=InfluencerStatus.ARCHIVED),
    )

    assert result.status == InfluencerStatus.ARCHIVED.value
    assert result.archived_at is not None
    assert repository.session.committed is True
