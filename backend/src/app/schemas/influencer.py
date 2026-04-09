"""Schemas for influencer CRUD requests and responses."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import InfluencerStatus


class InfluencerCreate(BaseModel):
    """Payload used to create a new influencer record."""

    slug: str = Field(min_length=3, max_length=120)
    display_name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    default_language: str = Field(default="en", min_length=2, max_length=16)
    primary_platform: str | None = Field(default=None, max_length=32)


class InfluencerUpdate(BaseModel):
    """Partial update payload for mutable influencer fields."""

    display_name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    default_language: str | None = Field(default=None, min_length=2, max_length=16)
    primary_platform: str | None = Field(default=None, max_length=32)
    status: InfluencerStatus | None = None


class InfluencerRead(BaseModel):
    """Serialized influencer resource returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    display_name: str
    status: str
    description: str | None
    default_language: str
    primary_platform: str | None
    provider_profile_id: UUID | None
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime


class InfluencerListResponse(BaseModel):
    """Paginated collection response for influencer listings."""

    items: list[InfluencerRead]
    total: int
