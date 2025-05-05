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
        host = settings.QDRANT_URL.replace("http://", "").split(":")[0]
        port = int(settings.QDRANT_URL.split(":")[-1])
        vector_store = VectorStore(host=host, port=port)
        logger.info("VectorStore initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing vector store: {str(e)}")
        raise

def get_vector_store() -> VectorStore:
    """Get the vector store instance."""
    return vector_store 