from app.services.vector_store import VectorStore
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize services
vector_store = None

async def init_vector_store():
    """Initialize the vector store service."""
    global vector_store
    
    try:
        # Initialize Vector Store
        vector_store = VectorStore(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        logger.info("VectorStore initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing vector store: {str(e)}")
        raise

def get_vector_store() -> VectorStore:
    """Get the vector store instance."""
    return vector_store 