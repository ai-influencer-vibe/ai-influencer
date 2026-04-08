import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Document(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    influencer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("influencer.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_uri: Mapped[str | None] = mapped_column(Text)
    mime_type: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    metadata: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)


class DocumentChunk(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __table_args__ = (UniqueConstraint("document_id", "chunk_index"),)

    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("document.id"))
    influencer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("influencer.id"))
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)
