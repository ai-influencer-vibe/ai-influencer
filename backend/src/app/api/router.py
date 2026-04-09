from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.influencers import router as influencer_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(influencer_router, prefix="/influencers", tags=["influencers"])
