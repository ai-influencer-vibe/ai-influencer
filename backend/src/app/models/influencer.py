import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import InfluencerStatus
from app.db.base import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ProviderProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    text_provider: Mapped[str] = mapped_column(String(64), nullable=False)
    image_provider: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding_provider: Mapped[str] = mapped_column(String(64), nullable=False)
    text_model: Mapped[str] = mapped_column(String(128), nullable=False)
    image_model: Mapped[str | None] = mapped_column(String(128))
    embedding_model: Mapped[str] = mapped_column(String(128), nullable=False)
    settings: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)

    influencers: Mapped[list["Influencer"]] = relationship(back_populates="provider_profile")


class Influencer(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default=InfluencerStatus.DRAFT.value, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text)
    default_language: Mapped[str] = mapped_column(String(16), default="en", nullable=False)
    primary_platform: Mapped[str | None] = mapped_column(String(32))
    provider_profile_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("provider_profile.id")
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    provider_profile: Mapped[ProviderProfile | None] = relationship(back_populates="influencers")
