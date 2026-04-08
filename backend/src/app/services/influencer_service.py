"""Influencer service scaffolding shared by future CRUD workflows."""

from __future__ import annotations

import uuid

from app.core.exceptions import ConflictError, NotFoundError
from app.models.influencer import Influencer
from app.repositories.influencer import InfluencerRepository


class InfluencerService:
    """Coordinate influencer business rules above raw repository access."""

    def __init__(self, repository: InfluencerRepository) -> None:
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
