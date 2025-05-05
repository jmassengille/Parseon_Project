import pytest
import numpy as np
from sentence_transformers import SentenceTransformer
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

@lru_cache()
def get_model():
    """Singleton pattern to load model only once"""
    return SentenceTransformer('all-MiniLM-L6-v2')

class TestEmbeddingsManager:
    def __init__(self):
        self.model = get_model()
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension

    async def create_embedding(self, text: str) -> list[float]:
        """Create embedding for a single text"""
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            raise

    async def create_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Create embeddings for a batch of texts"""
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error creating batch embeddings: {str(e)}")
            raise

    def calculate_similarity(self, embedding1: list[float], embedding2: list[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

    async def find_similar_patterns(
        self,
        query_text: str,
        pattern_embeddings: dict[str, list[float]],
        threshold: float = 0.7
    ) -> list[dict]:
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
        
        similar_patterns.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_patterns

@pytest.fixture
def embeddings_manager():
    return TestEmbeddingsManager()

@pytest.mark.asyncio
async def test_create_single_embedding(embeddings_manager):
    """Test creating a single embedding"""
    text = "This is a test document about security vulnerabilities"
    embedding = await embeddings_manager.create_embedding(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) == embeddings_manager.embedding_dim
    assert all(isinstance(x, float) for x in embedding)

@pytest.mark.asyncio
async def test_create_batch_embeddings(embeddings_manager):
    """Test creating embeddings in batch"""
    texts = [
        "This is a test document about security vulnerabilities",
        "Another document about API security testing",
        "Document discussing code injection attacks"
    ]
    embeddings = await embeddings_manager.create_embeddings_batch(texts)
    
    assert isinstance(embeddings, list)
    assert len(embeddings) == len(texts)
    for embedding in embeddings:
        assert len(embedding) == embeddings_manager.embedding_dim
        assert all(isinstance(x, float) for x in embedding)

def test_calculate_similarity(embeddings_manager):
    """Test similarity calculation between embeddings"""
    text1 = "Security vulnerability in API endpoints"
    text2 = "API security issues and vulnerabilities"
    
    embedding1 = embeddings_manager.model.encode(text1, convert_to_numpy=True).tolist()
    embedding2 = embeddings_manager.model.encode(text2, convert_to_numpy=True).tolist()
    
    similarity = embeddings_manager.calculate_similarity(embedding1, embedding2)
    
    assert isinstance(similarity, float)
    assert 0 <= similarity <= 1
    assert similarity > 0.7

@pytest.mark.asyncio
async def test_find_similar_patterns(embeddings_manager):
    """Test finding similar patterns"""
    patterns = {
        "sql_injection": "SQL injection vulnerability in database queries",
        "xss_attack": "Cross-site scripting (XSS) attack in web forms",
        "api_auth": "Missing API authentication checks",
        "unrelated": "Weather forecast for tomorrow"
    }
    
    pattern_embeddings = {}
    for pattern_id, text in patterns.items():
        embedding = await embeddings_manager.create_embedding(text)
        pattern_embeddings[pattern_id] = embedding
    
    query = "Check for SQL injection vulnerabilities in the database"
    results = await embeddings_manager.find_similar_patterns(
        query,
        pattern_embeddings,
        threshold=0.5
    )
    
    assert len(results) > 0
    assert results[0]["pattern_id"] == "sql_injection"
    assert results[0]["similarity"] > 0.7
    
    unrelated_results = [r for r in results if r["pattern_id"] == "unrelated"]
    assert len(unrelated_results) == 0 or unrelated_results[0]["similarity"] < 0.5

@pytest.mark.asyncio
async def test_model_caching():
    """Test that model is properly cached"""
    manager1 = TestEmbeddingsManager()
    manager2 = TestEmbeddingsManager()
    
    assert manager1.model is manager2.model 

# Real-world test cases based on actual assessment input
@pytest.mark.asyncio
async def test_code_vulnerability_detection(embeddings_manager):
    """Test detecting vulnerabilities in code snippets"""
    # Vulnerable code pattern
    vulnerable_code = """
    def process_prompt(user_input):
        # No input validation
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        return response.choices[0].message['content']
    """
    
    # Security patterns to match against
    security_patterns = {
        "input_validation": """
        Security issue: Code accepts and processes user input without proper validation.
        The user_input parameter is used directly without any sanitization or validation checks.
        This could lead to prompt injection or other security vulnerabilities.
        """,
        "error_handling": """
        Security issue: API calls lack proper error handling.
        The code makes external API calls without try-catch blocks or specific error handling.
        This could lead to unhandled exceptions and potential security issues.
        """,
        "prompt_injection": """
        Security issue: Raw user input is directly used in AI prompt.
        The code passes user input directly to the AI model without any sanitization.
        This creates a risk of prompt injection attacks and unexpected behavior.
        """,
        "unrelated": "Database connection pooling and configuration settings for PostgreSQL"
    }
    
    # Create embeddings for patterns
    pattern_embeddings = {}
    for pattern_id, text in security_patterns.items():
        embedding = await embeddings_manager.create_embedding(text)
        pattern_embeddings[pattern_id] = embedding
    
    # Test vulnerability detection with lower threshold
    results = await embeddings_manager.find_similar_patterns(
        vulnerable_code,
        pattern_embeddings,
        threshold=0.3  # Lower threshold for semantic matching
    )
    
    # Should detect input validation and prompt injection issues
    detected_issues = [r["pattern_id"] for r in results]
    assert "input_validation" in detected_issues
    assert "prompt_injection" in detected_issues
    assert "unrelated" not in detected_issues

@pytest.mark.asyncio
async def test_config_analysis(embeddings_manager):
    """Test analyzing configuration patterns"""
    # Test configuration
    config = """
    {
        "temperature": 0.9,
        "presence_penalty": 0.1,
        "frequency_penalty": 0.1,
        "max_tokens": null
    }
    """
    
    # Configuration patterns
    config_patterns = {
        "high_temperature": """
        Security risk: High temperature setting (0.9) in AI model configuration.
        Higher temperature values increase randomness and unpredictability in AI responses.
        This could lead to unexpected or potentially harmful outputs.
        """,
        "missing_token_limit": """
        Security risk: Missing or unlimited token limit in configuration.
        The max_tokens parameter is set to null, removing the safety limit.
        This could lead to excessive API usage, costs, or potential abuse.
        """,
        "rate_limiting": "API rate limiting and request throttling configuration",
        "unrelated": "Frontend UI component styling and theme configuration"
    }
    
    # Create embeddings for patterns
    pattern_embeddings = {}
    for pattern_id, text in config_patterns.items():
        embedding = await embeddings_manager.create_embedding(text)
        pattern_embeddings[pattern_id] = embedding
    
    # Test configuration analysis with lower threshold
    results = await embeddings_manager.find_similar_patterns(
        config,
        pattern_embeddings,
        threshold=0.3  # Lower threshold for semantic matching
    )
    
    # Should detect high temperature and missing token limit issues
    detected_issues = [r["pattern_id"] for r in results]
    assert "high_temperature" in detected_issues
    assert "missing_token_limit" in detected_issues
    assert "unrelated" not in detected_issues

@pytest.mark.asyncio
async def test_architecture_analysis(embeddings_manager):
    """Test analyzing architecture descriptions"""
    # Test architecture description
    architecture = """
    REST API endpoint that receives user input and forwards to OpenAI API.
    Basic authentication using API keys. No rate limiting implemented.
    Responses are cached in Redis for 1 hour.
    """
    
    # Architecture patterns
    arch_patterns = {
        "direct_forwarding": """
        Security risk: Direct request forwarding without validation layer.
        The API endpoint forwards requests directly to external AI services.
        This bypasses important security checks and validation steps.
        """,
        "basic_auth": """
        Security risk: Basic authentication mechanism.
        Using simple API key authentication without additional security layers.
        Consider implementing more robust authentication methods.
        """,
        "missing_rate_limit": """
        Security risk: No rate limiting implementation.
        The API lacks request rate limiting and throttling mechanisms.
        This could lead to abuse, DoS attacks, or excessive costs.
        """,
        "unrelated": "Frontend React component lifecycle and state management"
    }
    
    # Create embeddings for patterns
    pattern_embeddings = {}
    for pattern_id, text in arch_patterns.items():
        embedding = await embeddings_manager.create_embedding(text)
        pattern_embeddings[pattern_id] = embedding
    
    # Test architecture analysis with lower threshold
    results = await embeddings_manager.find_similar_patterns(
        architecture,
        pattern_embeddings,
        threshold=0.3  # Lower threshold for semantic matching
    )
    
    # Should detect architectural issues
    detected_issues = [r["pattern_id"] for r in results]
    assert "direct_forwarding" in detected_issues
    assert "missing_rate_limit" in detected_issues
    assert "basic_auth" in detected_issues
    assert "unrelated" not in detected_issues

@pytest.mark.asyncio
async def test_batch_processing_real_world(embeddings_manager):
    """Test batch processing with real-world inputs"""
    inputs = [
        # Code snippet
        """
        async def process_ai_request(prompt: str):
            response = await openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message['content']
        """,
        # Configuration
        """
        {
            "model": "gpt-3.5-turbo",
            "temperature": 0.8,
            "max_tokens": null,
            "presence_penalty": 0.0
        }
        """,
        # Architecture description
        """
        Serverless API endpoints deployed on Vercel.
        Uses Next.js API routes with basic JWT authentication.
        Direct integration with OpenAI API.
        """
    ]
    
    embeddings = await embeddings_manager.create_embeddings_batch(inputs)
    assert len(embeddings) == len(inputs)
    for embedding in embeddings:
        assert len(embedding) == embeddings_manager.embedding_dim

@pytest.mark.asyncio
async def test_model_caching():
    """Test that model is properly cached"""
    manager1 = TestEmbeddingsManager()
    manager2 = TestEmbeddingsManager()
    assert manager1.model is manager2.model 