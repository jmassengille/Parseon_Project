from fastapi.testclient import TestClient
from app.main import app

def test_assessment_endpoint():
    client = TestClient(app)
    test_input = {
        "organization_name": "Test Corp",
        "project_name": "API Test",
        "ai_provider": "openai",
        "configs": {
            "env_file": "OPENAI_API_KEY=sk-test\nMAX_REQUESTS=None",
            "json_config": '{"temperature": 0.9, "max_tokens": null}'
        },
        "implementation_details": {
            "prompt_handling": "Direct input without validation"
        },
        "architecture_description": "Simple API endpoint"
    }
    
    response = client.post("/api/v1/assessment/assess", json=test_input)
    assert response.status_code == 200
    result = response.json()
    
    assert "overall_score" in result
    assert "overall_risk_level" in result
    assert "vulnerabilities" in result 