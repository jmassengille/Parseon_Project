from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

@lru_cache()
def get_model():
    """Singleton pattern to load model only once"""
    return SentenceTransformer('all-MiniLM-L6-v2')

class EmbeddingsManager:
    def __init__(self):
        self.model = get_model()
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension

    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding for a single text"""
        try:
            # SentenceTransformer is synchronous, but fast enough locally
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            raise

    async def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a batch of texts"""
        try:
            # Batch processing is more efficient
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error creating batch embeddings: {str(e)}")
            raise

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

    async def find_similar_patterns(
        self,
        query_text: str,
        pattern_embeddings: Dict[str, List[float]],
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find similar patterns using embeddings"""
        query_embedding = await self.create_embedding(query_text)
        
        similar_patterns = []
        for pattern_id, pattern_embedding in pattern_embeddings.items():
            similarity = self.calculate_similarity(query_embedding, pattern_embedding)
            if similarity >= threshold:
                similar_patterns.append({
                    "pattern_id": pattern_id,
                    "similarity": similarity
                })
        
        # Sort by similarity score
        similar_patterns.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_patterns 