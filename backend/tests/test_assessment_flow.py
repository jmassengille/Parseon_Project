import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import get_db
from app.models.assessment import AssessmentRecord

# Test data
SAMPLE_ASSESSMENT_INPUT = {
    "organization_name": "Test Org",
    "project_name": "Test Project",
    "ai_provider": "openai",
    "configs": {
        "env_file": "OPENAI_API_KEY=sk-test\nMAX_TOKENS=500",
        "json_config": '{"temperature": 0.7}'
    },
    "implementation_details": {
        "prompt_handling": "def test(): pass"
    },
    "architecture_description": "Simple test architecture"
}

@pytest.fixture
def test_client():
    return TestClient(app)

def test_create_assessment(test_client):
    """Test the full assessment creation flow"""
    response = test_client.post("/api/v1/assess", json=SAMPLE_ASSESSMENT_INPUT)
    assert response.status_code == 200
    data = response.json()
    
    # Verify required fields
    assert "id" in data
    assert data["organization_name"] == SAMPLE_ASSESSMENT_INPUT["organization_name"]
    assert data["project_name"] == SAMPLE_ASSESSMENT_INPUT["project_name"]
    assert "overall_score" in data
    assert "vulnerabilities" in data
    
    # Verify database record
    db = next(get_db())
    record = db.query(AssessmentRecord).filter_by(id=data["id"]).first()
    assert record is not None
    assert record.organization_name == SAMPLE_ASSESSMENT_INPUT["organization_name"]

def test_get_assessment(test_client):
    """Test retrieving an assessment"""
    # First create an assessment
    response = test_client.post("/api/v1/assess", json=SAMPLE_ASSESSMENT_INPUT)
    assert response.status_code == 200
    assessment_id = response.json()["id"]
    
    # Then retrieve it
    response = test_client.get(f"/api/v1/assessments/{assessment_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == assessment_id

def test_error_handling(test_client):
    """Test error handling for invalid input"""
    # Test missing required field
    invalid_input = SAMPLE_ASSESSMENT_INPUT.copy()
    del invalid_input["organization_name"]
    response = test_client.post("/api/v1/assess", json=invalid_input)
    assert response.status_code == 422  # Validation error

    # Test invalid assessment ID
    response = test_client.get("/api/v1/assessments/99999")
    assert response.status_code == 404  # Not found 