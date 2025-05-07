from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/")
async def health_root():
    """
    Stateless health check endpoint for Railway deployment at /api/v1/health
    """
    return {
        "status": "healthy",
        "version": getattr(settings, "VERSION", "unknown"),
        "environment": getattr(settings, "ENVIRONMENT", "production"),
        "database": "not_configured"
    }

@router.get("/health")
async def health_check():
    """
    Stateless health check endpoint for Railway deployment
    """
    return {
        "status": "healthy",
        "version": getattr(settings, "VERSION", "unknown"),
        "environment": getattr(settings, "ENVIRONMENT", "production"),
        "database": "not_configured"
    } 