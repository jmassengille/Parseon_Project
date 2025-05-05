from typing import Generator
from app.db.session import AsyncSessionLocal
from app.services.vector_store import VectorStore
from app.core.vector_store_singleton import get_vector_store

async def get_db() -> Generator:
    """Dependency for getting SQLAlchemy session instance"""
    try:
        session = AsyncSessionLocal()
        yield session
    finally:
        await session.close()
        
def get_vector_store() -> VectorStore:
    """Dependency for getting VectorStore instance"""
    return vector_store 