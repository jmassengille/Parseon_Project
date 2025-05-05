from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import redis
import json
import os
from datetime import datetime
import logging
import torch

logger = logging.getLogger(__name__)

class EmbeddingsService:
    def __init__(self):
        # Initialize sentence transformer model
        self.model = None
        self.dimensions = 384  # Dimensions for all-MiniLM-L6-v2
        
        # Initialize Redis client
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis = redis.from_url(redis_url)
        
        # Cache settings
        self.cache_ttl = 86400  # 24 hours in seconds
    
    async def initialize(self):
        """Initialize the embeddings service and load the model"""
        try:
            if self.model is None:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Embeddings service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing embeddings service: {str(e)}")
            raise
    
    async def generate_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        """Generate embedding for text, using cache if available"""
        # Ensure model is initialized
        if self.model is None:
            await self.initialize()
        
        return self.get_embedding(text, use_cache)
        
    def get_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        """Get embedding for a text, using cache if available"""
        if use_cache:
            cached = self._get_from_cache(text)
            if cached:
                return cached
        
        try:
            # Generate embedding using sentence-transformers
            with torch.no_grad():
                embedding = self.model.encode(text, convert_to_tensor=False)
            
            if use_cache:
                self._save_to_cache(text, embedding)
            
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            raise
    
    def _get_from_cache(self, text: str) -> Optional[List[float]]:
        """Get embedding from Redis cache"""
        try:
            cached = self.redis.get(f"embedding:{text}")
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache retrieval error: {str(e)}")
        return None
    
    def _save_to_cache(self, text: str, embedding: List[float]):
        """Save embedding to Redis cache"""
        try:
            # Convert ndarray to list if necessary
            if hasattr(embedding, 'tolist'):
                embedding = embedding.tolist()
                
            self.redis.setex(
                f"embedding:{text}",
                self.cache_ttl,
                json.dumps(embedding)
            )
        except Exception as e:
            logger.warning(f"Cache save error: {str(e)}")
    
    def get_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        return self._cosine_similarity(emb1, emb2)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def find_similar_texts(self, query: str, texts: List[str], threshold: float = 0.7) -> List[Dict]:
        """Find texts similar to the query"""
        query_embedding = self.get_embedding(query)
        results = []
        
        for text in texts:
            text_embedding = self.get_embedding(text)
            similarity = self._cosine_similarity(query_embedding, text_embedding)
            
            if similarity >= threshold:
                results.append({
                    "text": text,
                    "similarity": float(similarity)
                })
        
        return sorted(results, key=lambda x: x["similarity"], reverse=True) 