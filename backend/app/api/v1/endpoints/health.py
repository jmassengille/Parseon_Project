from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings

router = APIRouter()

@router.get("")  # Root path for the health router
async def health_root(db: Session = Depends(get_db)):
    """
    Health check endpoint for Railway deployment at /api/v1/health
    This is the same as the /health endpoint but mounted at the router root
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for Railway deployment
    Tests database connection and basic configuration
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        } 