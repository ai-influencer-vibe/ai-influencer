"""Repository access helpers for influencer records."""

from __future__ import annotations

from sqlalchemy import func, select

from app.models.influencer import Influencer
from app.repositories.base import SQLAlchemyRepository


class InfluencerRepository(SQLAlchemyRepository[Influencer]):
    """Persistence operations specific to influencer aggregates."""

    model_type = Influencer

    def get_by_slug(self, slug: str) -> Influencer | None:
        """Return a single influencer by public slug."""

        statement = select(Influencer).where(Influencer.slug == slug)
        return self.session.scalar(statement)

    def count(self) -> int:
        """Return the total number of influencers stored in the database."""

        statement = select(func.count()).select_from(Influencer)
        return int(self.session.scalar(statement) or 0)
