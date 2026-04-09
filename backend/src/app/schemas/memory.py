"""Schemas for memory item and version workflows."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import MemoryType


class MemoryVersionCreate(BaseModel):
    """Payload used to create a new immutable memory version."""

    payload: dict[str, object]
    summary: str = Field(min_length=1)
    change_reason: str | None = None
    source: str = Field(min_length=1, max_length=32)
    created_by: str = Field(min_length=1, max_length=255)
    effective_at: datetime
    expires_at: datetime | None = None
    publish: bool = False


class MemoryItemCreate(BaseModel):
    """Payload used to create a logical memory item and its first version."""

    influencer_id: UUID
    memory_type: MemoryType
    subtype: str | None = Field(default=None, max_length=64)
    key: str = Field(min_length=1, max_length=128)
    title: str = Field(min_length=1, max_length=255)
    is_invariant: bool = False
    is_mutable: bool = True
    initial_version: MemoryVersionCreate


class MemoryVersionRead(BaseModel):
    """Serialized memory version returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    memory_item_id: UUID
    version: int
    status: str
    payload: dict[str, object]
    summary: str
    change_reason: str | None
    source: str
    source_generation_id: UUID | None
    created_by: str
    effective_at: datetime
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime


class MemoryItemRead(BaseModel):
    """Serialized logical memory item returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    influencer_id: UUID
    memory_type: str
    subtype: str | None
    key: str
    title: str
    is_invariant: bool
    is_mutable: bool
    current_version_id: UUID | None
    created_at: datetime
    updated_at: datetime


class MemoryItemDetailResponse(BaseModel):
    """Detailed memory response including historical versions."""

    item: MemoryItemRead
    versions: list[MemoryVersionRead]


class MemoryItemListResponse(BaseModel):
    """Collection response for influencer memory items."""

    items: list[MemoryItemRead]


class PublishMemoryVersionResponse(BaseModel):
    """Response returned after publishing a memory version."""

    item: MemoryItemRead
    version: MemoryVersionRead
