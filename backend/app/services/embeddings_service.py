from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import redis
import json
import os
from datetime import datetime
import logging
import torch
import hashlib
import tempfile

logger = logging.getLogger(__name__)

# Get temporary directory from main.py or use a default
TEMP_DIR = os.environ.get("TEMP_DIR", "/tmp/parseon_cache")

class EmbeddingsService:
    def __init__(self):
        # Initialize sentence transformer model
        self.model = None
        self.dimensions = 384  # Dimensions for all-MiniLM-L6-v2
        
        # Use TEMP_DIR for model cache
        os.environ["TORCH_HOME"] = os.path.join(TEMP_DIR, "torch")
        os.environ["TRANSFORMERS_CACHE"] = os.path.join(TEMP_DIR, "transformers")
        os.environ["HF_HOME"] = os.path.join(TEMP_DIR, "huggingface")
        
        # Initialize Redis client with robust error handling
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_available = False
        self.memory_cache = {}
        
        try:
            self.redis = redis.from_url(redis_url, socket_connect_timeout=2.0)
            # Test connection
            self.redis.ping()
            self.redis_available = True
            logger.info("Redis connection established successfully")
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.warning(f"Redis connection failed: {str(e)}. Using in-memory cache instead.")
        except Exception as e:
            logger.warning(f"Redis error: {str(e)}. Using in-memory cache instead.")
        
        # Cache settings
        self.cache_ttl = 86400  # 24 hours in seconds
        self.batch_size = 32  # Maximum batch size for embedding generation
        
        # Memory management settings
        self.max_cache_size = 500  # Max number of embeddings to keep in memory
    
    async def initialize(self):
        """Initialize the embeddings service and load the model"""
        try:
            if self.model is None:
                # Load model with memory-efficient settings for Railway
                logger.info("Loading sentence transformer model...")
                self.model = SentenceTransformer(
                    'all-MiniLM-L6-v2', 
                    cache_folder=os.path.join(TEMP_DIR, "models"),
                    device="cpu"  # Force CPU to avoid GPU memory issues on Railway
                )
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
    
    async def generate_embeddings_batch(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch for better performance"""
        # Ensure model is initialized
        if self.model is None:
            await self.initialize()
        
        if not texts:
            return []
        
        # Process texts in batches to avoid memory issues
        all_embeddings = []
        cache_hits = 0
        to_process = []
        to_process_indices = []
        
        # First check cache for each text
        if use_cache:
            for i, text in enumerate(texts):
                cached = self._get_from_cache(text)
                if cached is not None:
                    # Cache hit, add the cached embedding
                    all_embeddings.append(cached)
                    cache_hits += 1
                else:
                    # Cache miss, need to process
                    to_process.append(text)
                    to_process_indices.append(i)
            
            # Prepare results list with None placeholders
            result = [None] * len(texts)
            # Fill in cache hits
            for i, emb in enumerate(all_embeddings):
                result[i] = emb
        else:
            # No cache, process all
            to_process = texts
            to_process_indices = list(range(len(texts)))
            result = [None] * len(texts)
        
        # Process texts that weren't in cache
        if to_process:
            # Process in smaller batches for memory efficiency
            smaller_batch_size = min(16, self.batch_size)  # Smaller batches for Railway deployment
            
            for i in range(0, len(to_process), smaller_batch_size):
                batch = to_process[i:i+smaller_batch_size]
                indices = to_process_indices[i:i+smaller_batch_size]
                
                try:
                    # Generate embeddings for batch, ensuring we free memory after
                    with torch.no_grad():
                        embeddings = self.model.encode(batch, convert_to_tensor=True)
                        embeddings = embeddings.cpu().numpy()
                    
                    # Save to cache and result
                    for j, (text, embedding) in enumerate(zip(batch, embeddings)):
                        if use_cache:
                            self._save_to_cache(text, embedding)
                        result[indices[j]] = embedding.tolist()
                        
                    # Clear memory
                    if hasattr(embeddings, 'detach'):
                        del embeddings
                        torch.cuda.empty_cache() if torch.cuda.is_available() else None
                        
                except Exception as e:
                    logger.error(f"Error generating batch embeddings: {str(e)}")
                    # Fall back to individual processing if batch fails
                    for j, text in enumerate(batch):
                        try:
                            with torch.no_grad():
                                embedding = self.model.encode(text, convert_to_tensor=False)
                            if use_cache:
                                self._save_to_cache(text, embedding)
                            result[indices[j]] = embedding.tolist()
                        except Exception as inner_e:
                            logger.error(f"Error on individual embedding: {str(inner_e)}")
                            # Provide a fallback embedding
                            result[indices[j]] = [0.0] * self.dimensions
        
        # Clean memory cache if it gets too large
        if len(self.memory_cache) > self.max_cache_size:
            # Remove oldest 20% of entries
            prune_count = int(self.max_cache_size * 0.2)
            keys_to_remove = list(self.memory_cache.keys())[:prune_count]
            for key in keys_to_remove:
                del self.memory_cache[key]
            logger.info(f"Pruned {prune_count} embeddings from memory cache")
            
        return result
        
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
            # Use MD5 hash as key to avoid huge keys
            text_hash = hashlib.md5(text.encode()).hexdigest()
            cache_key = f"embedding:{text_hash}"
            
            if self.redis_available:
                try:
                    cached = self.redis.get(cache_key)
                    if cached:
                        return json.loads(cached)
                except (redis.ConnectionError, redis.TimeoutError) as e:
                    logger.warning(f"Redis connection error when getting from cache: {str(e)}")
                    self.redis_available = False  # Fallback to memory cache
                except Exception as e:
                    logger.warning(f"Redis error: {str(e)}")
            
            # Use in-memory cache if Redis not available
            if cache_key in self.memory_cache:
                return self.memory_cache[cache_key]
        except Exception as e:
            logger.warning(f"Cache retrieval error: {str(e)}")
        return None
    
    def _save_to_cache(self, text: str, embedding: List[float]):
        """Save embedding to Redis cache"""
        try:
            # Convert ndarray to list if necessary
            if hasattr(embedding, 'tolist'):
                embedding = embedding.tolist()
                
            # Use MD5 hash as key to avoid huge keys
            text_hash = hashlib.md5(text.encode()).hexdigest()
            cache_key = f"embedding:{text_hash}"
            
            if self.redis_available:
                try:
                    self.redis.setex(
                        cache_key,
                        self.cache_ttl,
                        json.dumps(embedding)
                    )
                except (redis.ConnectionError, redis.TimeoutError) as e:
                    logger.warning(f"Redis connection error when saving to cache: {str(e)}")
                    self.redis_available = False  # Fallback to memory cache
                    # Save to memory cache as fallback
                    self.memory_cache[cache_key] = embedding
                except Exception as e:
                    logger.warning(f"Redis error when saving: {str(e)}")
                    # Save to memory cache as fallback
                    self.memory_cache[cache_key] = embedding
            else:
                # Use in-memory cache if Redis not available
                self.memory_cache[cache_key] = embedding
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