"""
Main entry point for Parseon backend.
This file serves as an alternative entry point that redirects to app.main.
It's mainly for compatibility with different deployment platforms that might
use different conventions for locating the entry point.
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Ensure we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the actual application
    logger.info("Importing application from app.main")
    from app.main import app as application
    
    # Re-export the app for clarity
    app = application
    logger.info("Application imported successfully")
except Exception as e:
    logger.error(f"Error importing app: {str(e)}")
    # Create a minimal app for health check if main app fails to import
    from fastapi import FastAPI
    app = FastAPI(title="Parseon API (Fallback)")
    logger.info("Created fallback application")

# Add an alternative health check at the root level as a fallback
@app.get("/health")
async def health_check_root():
    """Fallback health check endpoint at the root level."""
    logger.info("Health check called at root level")
    return {
        "status": "healthy",
        "version": getattr(app.state, "VERSION", "0.1.0"),
        "service": "parseon-backend",
        "entry_point": "main.py",
        "timestamp": str(datetime.now().isoformat())
    }

# For direct execution
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    reload_mode = os.getenv("ENVIRONMENT", "development") == "development"
    logger.info(f"Starting uvicorn server on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=reload_mode) 