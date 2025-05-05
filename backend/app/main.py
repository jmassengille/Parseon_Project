from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import optional dependencies
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables
    logger.info("Loaded environment variables from .env file")
except ImportError:
    logger.warning("python-dotenv not installed, skipping .env loading")

# Create app first so health check always works
app = FastAPI(
    title="Parseon API",
    version=os.getenv("VERSION", "0.1.0"),
    openapi_url="/api/v1/openapi.json"
)

# Try to import settings, but provide fallbacks if it fails
try:
    from app.core.config import Settings
    settings = Settings()
    logger.info(f"Loaded settings: {settings.PROJECT_NAME} v{settings.VERSION}")
    
    # Set app version from settings
    app.title = settings.PROJECT_NAME
    app.version = settings.VERSION
except Exception as e:
    logger.error(f"Error loading settings: {str(e)}")
    logger.info("Using default settings")
    # Default settings for CORS
    BACKEND_CORS_ORIGINS = [
        "http://localhost:3000",
        "https://parseon.vercel.app",
        "*"
    ]

# Set up CORS
origins = getattr(settings, "BACKEND_CORS_ORIGINS", ["*"]) if "settings" in locals() else ["*"]

# If we have a wildcard in origins but also specific origins, we need to handle that specially
if "*" in origins and len(origins) > 1:
    # Remove the wildcard and keep the specific origins
    origins.remove("*")
    logger.warning("Both wildcard (*) and specific origins defined in CORS settings. Using specific origins only.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to include API router
try:
    from app.api.v1.api import api_router
    app.include_router(api_router, prefix="/api/v1")
    logger.info("API router loaded successfully")
except Exception as e:
    logger.error(f"Error including API router: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint that provides basic information about the API."""
    return {
        "message": "Welcome to Parseon API",
        "version": getattr(app.state, "VERSION", "0.1.0"),
        "docs_url": "/docs",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

# Simple health check that doesn't require database access
# This is the primary health check used by Railway
@app.get("/health")
async def health_check_simple():
    """Simple health check endpoint without database dependencies."""
    logger.info("Health check request received")
    return {
        "status": "healthy",
        "version": getattr(app.state, "VERSION", "0.1.0"),
        "service": "parseon-backend",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "timestamp": str(datetime.now().isoformat())
    }

@app.on_event("startup")
async def startup_event():
    """Initialize application dependencies on startup."""
    try:
        # Try to initialize rate limiter
        try:
            from app.core.rate_limiter import init_rate_limiter
            await init_rate_limiter()
            logger.info("Rate limiter initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize rate limiter: {str(e)}")
        
        # Try to initialize Vector Store
        try:
            from app.core.vector_store_singleton import init_vector_store
            await init_vector_store()
            logger.info("Vector store initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize vector store: {str(e)}")
        
        logger.info(f"Starting Parseon backend service: {app.version}")
        logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'production')}")
        logger.info("Parseon API started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        # Don't raise to avoid startup failure, just log the error
        
# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("app.main:app", host=host, port=port, reload=os.getenv("ENVIRONMENT", "") == "development") 