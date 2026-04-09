"""Versioned memory endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_request_db_session
from app.repositories.memory import MemoryItemRepository, MemoryVersionRepository
from app.schemas.memory import (
    MemoryItemCreate,
    MemoryItemDetailResponse,
    MemoryItemListResponse,
    MemoryVersionCreate,
    MemoryVersionRead,
    PublishMemoryVersionResponse,
)
from app.services.memory_service import MemoryService

router = APIRouter()


def get_memory_service(
    session: Annotated[Session, Depends(get_request_db_session)],
) -> MemoryService:
    """Build a memory service for the current request scope."""

    return MemoryService(
        memory_items=MemoryItemRepository(session=session),
        memory_versions=MemoryVersionRepository(session=session),
    )


@router.get("/", response_model=MemoryItemListResponse)
async def list_memory_items(
    influencer_id: Annotated[UUID, Query()],
    service: Annotated[MemoryService, Depends(get_memory_service)],
) -> MemoryItemListResponse:
    """List all memory items for one influencer."""

    items = service.list_influencer_memory(influencer_id)
    return MemoryItemListResponse(items=items)


@router.post("/", response_model=MemoryItemDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_memory_item(
    payload: MemoryItemCreate,
    service: Annotated[MemoryService, Depends(get_memory_service)],
) -> MemoryItemDetailResponse:
    """Create a memory item and its initial immutable version."""

    result = service.create_memory_item(payload)
    return MemoryItemDetailResponse(item=result.item, versions=result.versions)


@router.get("/{memory_item_id}", response_model=MemoryItemDetailResponse)
async def get_memory_item(
    memory_item_id: UUID,
    service: Annotated[MemoryService, Depends(get_memory_service)],
) -> MemoryItemDetailResponse:
    """Return one memory item with its version history."""

    result = service.get_memory_detail(memory_item_id)
    return MemoryItemDetailResponse(item=result.item, versions=result.versions)


@router.post("/{memory_item_id}/versions", response_model=MemoryVersionRead, status_code=status.HTTP_201_CREATED)
async def create_memory_version(
    memory_item_id: UUID,
    payload: MemoryVersionCreate,
    service: Annotated[MemoryService, Depends(get_memory_service)],
) -> MemoryVersionRead:
    """Create a new version for an existing memory item."""

    return service.create_memory_version(memory_item_id, payload)


@router.post("/{memory_item_id}/versions/{version_id}/publish", response_model=PublishMemoryVersionResponse)
async def publish_memory_version(
    memory_item_id: UUID,
    version_id: UUID,
    service: Annotated[MemoryService, Depends(get_memory_service)],
) -> PublishMemoryVersionResponse:
    """Publish a memory version and make it the current active revision."""

    result = service.publish_memory_version(memory_item_id, version_id)
    return PublishMemoryVersionResponse(item=result.item, version=result.version)
