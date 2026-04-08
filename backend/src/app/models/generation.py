import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin


class GenerationRequest(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    influencer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("influencer.id"))
    content_type: Mapped[str] = mapped_column(String(64), nullable=False)
    platform: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    requested_by: Mapped[str] = mapped_column(String(255), nullable=False)
    input_payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    provider_profile_snapshot: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    prompt_template_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))


class GenerationContext(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    generation_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generation_request.id"), nullable=False
    )
    context_pack: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    token_budget: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    retrieval_trace: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)


class GenerationOutput(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __table_args__ = (UniqueConstraint("generation_request_id", "attempt_number"),)

    generation_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generation_request.id"), nullable=False
    )
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    raw_output: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_output: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    output_text: Mapped[str | None] = mapped_column(Text)
    asset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("asset.id"))
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536))


class ValidationResult(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    generation_output_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generation_output.id"), nullable=False
    )
    validator_name: Mapped[str] = mapped_column(String(64), nullable=False)
    passed: Mapped[bool] = mapped_column(nullable=False)
    score: Mapped[float | None] = mapped_column(Numeric(5, 4))
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    details: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
