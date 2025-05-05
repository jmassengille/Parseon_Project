from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from app.core.config import settings
import logging
from fastapi import Depends

logger = logging.getLogger(__name__)

async def init_rate_limiter():
    """Initialize the rate limiter with Redis."""
    if settings.ENVIRONMENT == "development":
        logger.info("Rate limiter disabled in development mode")
        return
        
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        await FastAPILimiter.init(redis_client)
        logger.info("Rate limiter initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize rate limiter: {str(e)}")
        if settings.ENVIRONMENT == "production":
            raise
        logger.warning("Continuing without rate limiter in development mode")

# Rate limit decorators
def rate_limit(requests: int = 60, period: int = 60):
    """
    Rate limit decorator for endpoints.
    
    Args:
        requests: Number of requests allowed in the period
        period: Time period in seconds
    """
    if settings.ENVIRONMENT == "development":
        return lambda: None  # No-op in development
    return Depends(RateLimiter(times=requests, seconds=period)) 