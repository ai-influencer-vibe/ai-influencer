"""Influencer service scaffolding shared by future CRUD workflows."""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

from app.core.enums import InfluencerStatus
from app.core.exceptions import ConflictError, NotFoundError
from app.models.influencer import Influencer
from app.schemas.influencer import InfluencerCreate, InfluencerUpdate


@dataclass(slots=True)
class InfluencerListResult:
    """Typed container for paginated influencer listings."""

    items: list[Influencer]
    total: int


class InfluencerRepositoryProtocol(Protocol):
    """Protocol describing the repository behavior required by the service."""

    session: Any

    def get(self, entity_id: uuid.UUID) -> Influencer | None:
        """Return one influencer by identifier."""

    def get_by_slug(self, slug: str) -> Influencer | None:
        """Return one influencer by slug."""

    def list(self, limit: int = 100, offset: int = 0) -> list[Influencer]:
        """Return a paginated set of influencers."""

    def count(self) -> int:
        """Return the total number of influencers."""

    def add(self, instance: Influencer) -> Influencer:
        """Persist an influencer instance."""


class InfluencerService:
    """Coordinate influencer business rules above raw repository access."""

    def __init__(self, repository: InfluencerRepositoryProtocol) -> None:
        """Create a service bound to an influencer repository."""

        self.repository = repository

    def get_or_raise(self, influencer_id: uuid.UUID) -> Influencer:
        """Return one influencer or raise a typed not-found error."""

        influencer = self.repository.get(influencer_id)
        if influencer is None:
            raise NotFoundError("Influencer", {"influencer_id": str(influencer_id)})
        return influencer

    def ensure_slug_available(self, slug: str) -> None:
        """Reject duplicate public slugs before a write occurs."""

        if self.repository.get_by_slug(slug) is not None:
            raise ConflictError(
                message="An influencer with this slug already exists.",
                details={"slug": slug},
            )

    def list_influencers(self, limit: int = 100, offset: int = 0) -> InfluencerListResult:
        """Return a paginated list of influencers and the current total count."""

        return InfluencerListResult(
            items=self.repository.list(limit=limit, offset=offset),
            total=self.repository.count(),
        )

    def create_influencer(self, payload: InfluencerCreate) -> Influencer:
        """Create and persist a new influencer after enforcing uniqueness rules."""

        self.ensure_slug_available(payload.slug)
        influencer = Influencer(
            slug=payload.slug,
            display_name=payload.display_name,
            description=payload.description,
            default_language=payload.default_language,
            primary_platform=payload.primary_platform,
            status=InfluencerStatus.DRAFT.value,
        )
        self.repository.add(influencer)
        self.repository.session.commit()
        self.repository.session.refresh(influencer)
        return influencer

    def update_influencer(
        self,
        influencer_id: uuid.UUID,
        payload: InfluencerUpdate,
    ) -> Influencer:
        """Apply a partial update to an influencer and persist the changes."""

        influencer = self.get_or_raise(influencer_id)
        changes = payload.model_dump(exclude_unset=True)

        for field_name, value in asdict(_normalize_update_payload(changes)).items():
            if value is _UNSET:
                continue
            setattr(influencer, field_name, value)

        if influencer.status == InfluencerStatus.ARCHIVED.value:
            influencer.archived_at = influencer.archived_at or datetime.now(UTC)
        elif "status" in changes:
            influencer.archived_at = None

        self.repository.session.add(influencer)
        self.repository.session.commit()
        self.repository.session.refresh(influencer)
        return influencer


class _UnsetType:
    """Sentinel that differentiates omitted update fields from explicit nulls."""


_UNSET = _UnsetType()


@dataclass(slots=True)
class _NormalizedInfluencerUpdate:
    """Normalized influencer update payload with omission tracking."""

    display_name: str | None | _UnsetType = _UNSET
    description: str | None | _UnsetType = _UNSET
    default_language: str | None | _UnsetType = _UNSET
    primary_platform: str | None | _UnsetType = _UNSET
    status: str | None | _UnsetType = _UNSET


def _normalize_update_payload(changes: dict[str, object]) -> _NormalizedInfluencerUpdate:
    """Convert a partial Pydantic payload into a sentinel-aware dataclass."""

    normalized = _NormalizedInfluencerUpdate()
    for key, value in changes.items():
        if key == "status" and value is not None:
            setattr(normalized, key, value.value if isinstance(value, InfluencerStatus) else value)
        else:
            setattr(normalized, key, value)
    return normalized
