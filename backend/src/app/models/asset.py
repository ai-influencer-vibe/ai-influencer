import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Asset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    influencer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("influencer.id"))
    asset_type: Mapped[str] = mapped_column(String(32), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    metadata: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)


class AssetGeneration(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    asset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("asset.id"))
    influencer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("influencer.id"))
    generation_request_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    negative_prompt: Mapped[str | None] = mapped_column(Text)
    parameters: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
    seed: Mapped[str | None] = mapped_column(String(64))


class AssetEmbedding(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __table_args__ = (UniqueConstraint("asset_id", "embedding_model"),)

    asset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("asset.id"))
    influencer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("influencer.id"))
    embedding_model: Mapped[str] = mapped_column(String(128), nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)
    metadata: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
