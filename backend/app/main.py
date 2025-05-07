from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
import os
import sys
import traceback
import time
from fastapi.responses import JSONResponse
from app.api.v1.api import router as api_router
from app.core.config import settings
from app.core.exceptions import AssessmentError
from app.services.assessment_service import SecurityAssessmentService, _base_analyzer, _embedding_service, _finding_validator
from app.services.embeddings_service import EmbeddingsService
from app.core.base_model_analyzer import BaseModelAnalyzer
from app.core.finding_validator import FindingValidator
from app.core.knowledge_base import KnowledgeBase
import asyncio
import signal
import tempfile
import shutil

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

# Create temp directory for caching that works with Railway's ephemeral filesystem
TEMP_DIR = os.environ.get("TEMP_DIR", "/tmp/parseon_cache")
os.makedirs(TEMP_DIR, exist_ok=True)
os.environ["TORCH_HOME"] = os.path.join(TEMP_DIR, "torch")
os.environ["TRANSFORMERS_CACHE"] = os.path.join(TEMP_DIR, "transformers")
os.environ["HF_HOME"] = os.path.join(TEMP_DIR, "huggingface")
logger.info(f"Using temporary directory for caching: {TEMP_DIR}")

# Create app first so health check always works
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=os.getenv("VERSION", "0.1.0"),
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup
ENV = os.getenv("ENVIRONMENT", "development")

if ENV == "production":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://parseon.tech",
            "https://www.parseon.tech", 
            "https://frontend-parseon.vercel.app",  # Add Vercel frontend
            "*"  # Allow all origins temporarily for testing
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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

# Try to include API router
try:
    from app.api.v1.api import router as api_router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    logger.info("API router loaded successfully")
except Exception as e:
    logger.error(f"Error including API router: {str(e)}")
    logger.error(traceback.format_exc())

@app.exception_handler(AssessmentError)
async def assessment_error_handler(request: Request, exc: AssessmentError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )

# Add better error handling for generic errors
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected error occurred",
            "detail": str(exc) if ENV != "production" else "Internal Server Error"
        }
    )

# Performance middleware to log request duration
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log long-running requests for performance monitoring
        if process_time > 5.0:
            logger.warning(f"Long request: {request.url.path} took {process_time:.2f} seconds")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Error during request: {request.url.path} after {process_time:.2f} seconds: {str(e)}")
        raise

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

# Early initialization of services to avoid cold start
async def initialize_services():
    """Initialize services during startup to avoid request-time delays"""
    try:
        global _base_analyzer, _embedding_service, _finding_validator
        
        # Initialize base analyzer if needed
        if _base_analyzer is None:
            logger.info("Pre-initializing BaseModelAnalyzer")
            _base_analyzer = BaseModelAnalyzer()
        
        # Initialize embedding service first, as it's needed by the validator
        if _embedding_service is None:
            logger.info("Pre-initializing EmbeddingsService")
            _embedding_service = EmbeddingsService()
            await _embedding_service.initialize()
        
        # Initialize finding validator with simple knowledge base
        if _finding_validator is None:
            logger.info("Pre-initializing FindingValidator")
            empty_kb = KnowledgeBase() 
            _finding_validator = FindingValidator(knowledge_base=empty_kb)
            await _finding_validator.initialize()
            
        logger.info("Service initialization complete")
    except Exception as e:
        logger.error(f"Error initializing services during startup: {str(e)}")

# Setup graceful shutdown for Railway
async def shutdown_event():
    """Clean up resources on application shutdown"""
    logger.info("Application shutdown in progress")
    
    try:
        # Clean up any temporary files
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR, ignore_errors=True)
            logger.info(f"Removed temporary directory: {TEMP_DIR}")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
    
    logger.info("Shutdown complete")

@app.on_event("startup")
async def startup_event():
    """Run initialization during startup"""
    logger.info("Application startup")
    
    # Log environment and timeout settings for observability
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'production')}")
    
    # Import timeout settings to log them
    from app.services.assessment_service import ANALYSIS_TIMEOUT, VALIDATION_TIMEOUT, API_CALL_TIMEOUT
    logger.info(f"Timeout settings: Analysis={ANALYSIS_TIMEOUT}s, Validation={VALIDATION_TIMEOUT}s, API={API_CALL_TIMEOUT}s")
    
    await initialize_services()
    
    # Pre-warm other services
    assessment_service = SecurityAssessmentService()
    await assessment_service._ensure_initialized()

# Register shutdown event
@app.on_event("shutdown")
async def shutdown():
    await shutdown_event()

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Handle graceful shutdown for Ctrl+C
    def handle_sigterm(*args):
        logger.info("SIGTERM received, shutting down")
        sys.exit(0)
        
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)
    
    # Start the server
    uvicorn.run("app.main:app", host=host, port=port, reload=os.getenv("ENVIRONMENT", "") == "development") 