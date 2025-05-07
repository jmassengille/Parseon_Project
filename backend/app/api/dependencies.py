from app.services.vector_store import VectorStore
from app.core.vector_store_singleton import get_vector_store

# Removed all database session management code. Only vector store dependency remains.

def get_vector_store() -> VectorStore:
    """Dependency for getting VectorStore instance"""
    return get_vector_store() 