import pytest
from fastapi.testclient import TestClient
import os
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Dict, List
import asyncio

# Only import app if we're not running standalone tests
if os.getenv("TEST_STANDALONE") != "true":
    try:
        from app.main import app
    except Exception as e:
        print(f"Warning: Could not import app: {e}")
        app = None

@pytest.fixture
def client():
    if app is None:
        pytest.skip("App not available")
    return TestClient(app)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def embedding_model():
    """Provide a sentence transformer model for testing."""
    return SentenceTransformer('all-MiniLM-L6-v2')

@pytest.fixture
def sample_embeddings(embedding_model) -> Dict[str, List[float]]:
    """Generate sample embeddings for testing."""
    texts = [
        "Security vulnerability in API endpoints",
        "Missing input validation in user data",
        "Potential prompt injection risk",
        "Insecure model configuration settings"
    ]
    
    embeddings = embedding_model.encode(texts)
    return {
        f"pattern_{i}": embedding.tolist()
        for i, embedding in enumerate(embeddings)
    }

@pytest.fixture
def sample_security_patterns() -> List[Dict]:
    """Provide sample security patterns for testing."""
    return [
        {
            "id": "prompt_injection",
            "description": "Vulnerability to prompt injection attacks",
            "severity": "CRITICAL",
            "category": "code"
        },
        {
            "id": "model_security",
            "description": "Insecure model configuration",
            "severity": "HIGH",
            "category": "model"
        }
    ] 