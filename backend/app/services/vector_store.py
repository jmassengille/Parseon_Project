from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Service for managing document embeddings in Qdrant vector database.
    
    This service handles:
    - Document storage and retrieval
    - Similarity search
    - Collection management
    """
    
    COLLECTION_NAME = "security_assessments"
    VECTOR_SIZE = 384  # Size of all-MiniLM-L6-v2 embeddings
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        """
        Initialize the vector store with Qdrant client.
        
        Args:
            host: Qdrant server host
            port: Qdrant server port
        """
        try:
            self.client = QdrantClient(host=host, port=port)
            self._ensure_collection_exists()
            logger.info(f"Initialized vector store with Qdrant at {host}:{port}")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            raise
    
    def _ensure_collection_exists(self):
        """Ensure the collection exists, create if it doesn't"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if self.COLLECTION_NAME not in collection_names:
                self.client.create_collection(
                    collection_name=self.COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=self.VECTOR_SIZE,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.COLLECTION_NAME}")
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {str(e)}")
            raise
    
    async def store_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Store document embeddings in the vector store.
        
        Args:
            documents: List of documents with embeddings
            
        Returns:
            bool: True if successful
        """
        if not documents:
            return True
            
        try:
            points = []
            for doc in documents:
                point = models.PointStruct(
                    id=doc["id"],
                    vector=doc["embedding"],
                    payload={
                        "content": doc["content"],
                        "metadata": doc["metadata"],
                        "created_at": doc["created_at"].isoformat()
                    }
                )
                points.append(point)
            
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=points
            )
            
            logger.info(f"Stored {len(documents)} documents in vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error storing documents: {str(e)}")
            raise
    
    async def search_similar(
        self,
        query_embedding: List[float],
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using a query embedding.
        
        Args:
            query_embedding: Query vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of similar documents with scores
        """
        try:
            search_result = self.client.search(
                collection_name=self.COLLECTION_NAME,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )
            
            results = []
            for scored_point in search_result:
                result = {
                    "id": scored_point.id,
                    "score": scored_point.score,
                    "content": scored_point.payload["content"],
                    "metadata": scored_point.payload["metadata"],
                    "created_at": datetime.fromisoformat(scored_point.payload["created_at"])
                }
                results.append(result)
            
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar documents: {str(e)}")
            raise
    
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """
        Delete documents from the vector store.
        
        Args:
            document_ids: List of document IDs to delete
            
        Returns:
            bool: True if successful
        """
        try:
            self.client.delete(
                collection_name=self.COLLECTION_NAME,
                points_selector=models.PointIdsList(
                    points=document_ids
                )
            )
            
            logger.info(f"Deleted {len(document_ids)} documents from vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise 