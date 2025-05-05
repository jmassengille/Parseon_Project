import pytest
import asyncio
import os
from dotenv import load_dotenv
from app.services.assessment_service import SecurityAssessmentService
from app.schemas.assessment_input import SecurityAssessmentInput, ConfigType, ScanMode
from app.schemas.assessment import RiskLevel

# Load environment variables
load_dotenv()

# Test data
VULNERABLE_CODE = """
def process_user_input(user_input):
    # Direct prompt forwarding without sanitization
    prompt = f"You are a helpful assistant. Answer this: {user_input}"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    try:
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred"
"""

EXAMPLE_CONFIG = """
{
    "model": "gpt-3.5-turbo",
    "temperature": 0.9,
    "max_tokens": 2000
}
"""

@pytest.fixture
async def assessment_service():
    """Create and initialize assessment service for tests"""
    service = SecurityAssessmentService()
    await service.initialize()
    return service

@pytest.mark.asyncio
async def test_full_assessment(assessment_service):
    """Test complete assessment flow with multiple components"""
    # Create assessment input
    assessment_input = SecurityAssessmentInput(
        organization_name="Test Organization",
        project_name="Test Project",
        ai_provider="openai",
        scan_mode=ScanMode.COMPREHENSIVE,
        implementation_details={
            "process_function": VULNERABLE_CODE
        },
        configs={
            ConfigType.JSON_CONFIG: EXAMPLE_CONFIG
        },
        architecture_description="Test architecture for a chatbot application"
    )
    
    # Run assessment
    result = await assessment_service.analyze_input(assessment_input)
    
    # Basic assertions
    assert result.organization_name == "Test Organization"
    assert result.project_name == "Test Project"
    assert result.overall_score <= 100.0
    assert result.overall_risk_level in [r for r in RiskLevel]
    
    # Check that we have findings
    assert len(result.vulnerabilities) > 0, "Should have at least one vulnerability finding"
    
    # Check that category scores exist
    assert len(result.category_scores) > 0
    
    # Check priority actions
    assert len(result.priority_actions) > 0
    
    print(f"Found {len(result.vulnerabilities)} vulnerabilities")
    print(f"Overall score: {result.overall_score}")
    print(f"Risk level: {result.overall_risk_level}")

@pytest.mark.asyncio
async def test_finding_validation(assessment_service):
    """Test that findings are properly validated"""
    # Create assessment input with known vulnerability
    assessment_input = SecurityAssessmentInput(
        organization_name="Test Organization",
        project_name="Test Project",
        ai_provider="openai",
        scan_mode=ScanMode.PROMPT_SECURITY,  # Focus on prompt security
        implementation_details={
            "process_function": VULNERABLE_CODE  # Contains prompt injection vulnerability
        }
    )
    
    # Run assessment
    result = await assessment_service.analyze_input(assessment_input)
    
    # Check for prompt injection vulnerability
    prompt_injection_found = False
    for vuln in result.vulnerabilities:
        if "prompt" in vuln.title.lower() and "injection" in vuln.title.lower():
            prompt_injection_found = True
            # Check that it has validation info
            assert vuln.validation_info is not None, "Validation info should be present"
            assert vuln.validation_info.get("validation_score", 0) > 0.5, "Should have reasonable validation score"
            assert vuln.validation_info.get("validated", False) is True, "Should be validated"
            break
    
    assert prompt_injection_found, "Should detect prompt injection vulnerability"
    
    # Verify that at least one finding has validation info
    assert any(v.validation_info for v in result.vulnerabilities), "At least one vulnerability should have validation info"
    
    print(f"Found {len(result.vulnerabilities)} vulnerabilities")
    print(f"Validated findings: {sum(1 for v in result.vulnerabilities if v.validation_info and v.validation_info.get('validated', False))}")

if __name__ == "__main__":
    asyncio.run(test_full_assessment(SecurityAssessmentService())) 