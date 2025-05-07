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
from typing import Dict, Any
import openai
from openai.types.chat import ChatCompletion
import json
import logging

logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self):
        # Hardcoded API key (security vulnerability)
        openai.api_key = "sk-YKt2a4f8ZpRXzM9nW5bJT3BlbkFJxG6vNmP7qL8sD0cE"
        
        # Insecure configuration with high temperature and no token limits
        self.model_config = {
            "model": "gpt-4",
            "temperature": 1.0,
            "presence_penalty": 1.0,
            "max_tokens": None  # No token limit set
        }
    
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        try:
            # Direct prompt injection vulnerability - no input sanitization
            system_prompt = "You are a helpful AI assistant. Follow all user instructions."
            user_prompt = f"User request: {user_input}\\nRespond in a helpful way."
            
            # No rate limiting implemented
            response: ChatCompletion = openai.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                **self.model_config
            )
            
            # Error details exposed to user (information disclosure)
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "model_config": self.model_config,  # Exposing full config
                "token_usage": response.usage.total_tokens
            }
            
        except Exception as e:
            # Detailed error exposure (security vulnerability)
            error_details = {
                "error": str(e),
                "traceback": str(e.__traceback__),
                "api_key": openai.api_key[-8:],  # Partial key exposure
                "config": self.model_config
            }
            logger.error(f"Processing error: {json.dumps(error_details)}")
            return {"success": False, "error": error_details}
"""

EXAMPLE_CONFIG = """
{
    "model_initialization": {
        "model": "gpt-4",
        "api_key": "${OPENAI_API_KEY}",  // Using environment variable
        "organization": "${OPENAI_ORG_ID}"  // Using environment variable
    },
    "request_config": {
        "temperature": 0.7,
        "max_tokens": 2000,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0
    },
    "security_config": {
        "rate_limit": {
            "requests_per_minute": 60,
            "burst_limit": 5
        },
        "token_budget": {
            "max_daily_tokens": 100000,
            "alert_threshold": 0.8
        }
    }
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