"""Health endpoints used for runtime checks and smoke tests."""

from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def healthcheck() -> HealthResponse:
    """Return a minimal API health response."""

    return HealthResponse(status="ok")
