from fastapi import APIRouter
from app.api.v1.endpoints import assessment, health  # Add health endpoint

router = APIRouter()
router.include_router(assessment.router, tags=["assessment"])
router.include_router(health.router, prefix="/health", tags=["health"])