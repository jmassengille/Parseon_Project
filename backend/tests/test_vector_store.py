import pytest
from app.services.vector_store import VectorStore
from datetime import datetime
import numpy as np

@pytest.fixture
def vector_store():
    return VectorStore()

@pytest.fixture
def sample_documents():
    return [
        {
            "id": "test1",
            "content": "Security vulnerability in API endpoints",
            "metadata": {"type": "test"},
            "embedding": np.random.rand(384).tolist(),  # Mock embedding
            "created_at": datetime.utcnow()
        },
        {
            "id": "test2",
            "content": "API security best practices",
            "metadata": {"type": "test"},
            "embedding": np.random.rand(384).tolist(),  # Mock embedding
            "created_at": datetime.utcnow()
        }
    ]

@pytest.mark.asyncio
async def test_store_documents(vector_store, sample_documents):
    """Test document storage"""
    result = await vector_store.store_documents(sample_documents)
    assert result is True

@pytest.mark.asyncio
async def test_search_similar(vector_store, sample_documents):
    """Test similarity search"""
    # First store the documents
    await vector_store.store_documents(sample_documents)
    
    # Search using the first document's embedding
    results = await vector_store.search_similar(
        query_embedding=sample_documents[0]["embedding"],
        limit=2
    )
    
    assert len(results) > 0
    assert "id" in results[0]
    assert "score" in results[0]
    assert "content" in results[0]
    assert "metadata" in results[0]

@pytest.mark.asyncio
async def test_delete_documents(vector_store, sample_documents):
    """Test document deletion"""
    # First store the documents
    await vector_store.store_documents(sample_documents)
    
    # Delete the documents
    result = await vector_store.delete_documents([doc["id"] for doc in sample_documents])
    assert result is True
    
    # Verify deletion by searching
    results = await vector_store.search_similar(
        query_embedding=sample_documents[0]["embedding"],
        limit=2
    )
    assert len(results) == 0

@pytest.mark.asyncio
async def test_empty_documents(vector_store):
    """Test handling of empty document list"""
    result = await vector_store.store_documents([])
    assert result is True 