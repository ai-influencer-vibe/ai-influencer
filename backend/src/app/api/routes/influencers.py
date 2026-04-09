"""Influencer CRUD endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_request_db_session
from app.repositories.influencer import InfluencerRepository
from app.schemas.influencer import (
    InfluencerCreate,
    InfluencerListResponse,
    InfluencerRead,
    InfluencerUpdate,
)
from app.services.influencer_service import InfluencerService

router = APIRouter()


def get_influencer_service(
    session: Annotated[Session, Depends(get_request_db_session)],
) -> InfluencerService:
    """Build an influencer service for the current request scope."""

    repository = InfluencerRepository(session=session)
    return InfluencerService(repository=repository)


@router.get("/", response_model=InfluencerListResponse)
async def list_influencers(
    service: Annotated[InfluencerService, Depends(get_influencer_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> InfluencerListResponse:
    """List influencers with basic pagination metadata."""

    result = service.list_influencers(limit=limit, offset=offset)
    return InfluencerListResponse(items=result.items, total=result.total)


@router.post("/", response_model=InfluencerRead, status_code=status.HTTP_201_CREATED)
async def create_influencer(
    payload: InfluencerCreate,
    service: Annotated[InfluencerService, Depends(get_influencer_service)],
) -> InfluencerRead:
    """Create a new influencer resource."""

    return service.create_influencer(payload)


@router.get("/{influencer_id}", response_model=InfluencerRead)
async def get_influencer(
    influencer_id: UUID,
    service: Annotated[InfluencerService, Depends(get_influencer_service)],
) -> InfluencerRead:
    """Return one influencer by identifier."""

    return service.get_or_raise(influencer_id)


@router.patch("/{influencer_id}", response_model=InfluencerRead)
async def update_influencer(
    influencer_id: UUID,
    payload: InfluencerUpdate,
    service: Annotated[InfluencerService, Depends(get_influencer_service)],
) -> InfluencerRead:
    """Apply a partial update to an influencer resource."""

    return service.update_influencer(influencer_id, payload)
