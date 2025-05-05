"""
Test to verify the new Parseon architecture using base model analysis and finding validation
"""

import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.base_model_analyzer import BaseModelAnalyzer
from app.core.finding_validator import FindingValidator
from app.schemas.assessment_input import SecurityAssessmentInput, ScanMode, ConfigType
from app.services.assessment_service import SecurityAssessmentService
from app.core.knowledge_base import KnowledgeBase

# Load environment variables
load_dotenv()

# Test code with prompt injection vulnerability
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

async def test_new_architecture():
    """Test the integration of BaseModelAnalyzer and FindingValidator"""
    print("\n=== TESTING NEW PARSEON ARCHITECTURE ===\n")
    
    # Create instances of our components
    base_analyzer = BaseModelAnalyzer()
    finding_validator = FindingValidator(knowledge_base=KnowledgeBase())
    
    # Initialize the validator
    await finding_validator.initialize()
    
    # 1. First test BaseModelAnalyzer directly
    print("1. Testing BaseModelAnalyzer directly...")
    base_findings = await base_analyzer.analyze_code(VULNERABLE_CODE, "process_user_input")
    
    print(f"\nBase Model Findings: {len(base_findings)}")
    for finding in base_findings:
        print(f"  - {finding.title} ({finding.severity}): {finding.confidence}")
        print(f"    {finding.description[:150]}...\n")
    
    # 2. Next test with FindingValidator integration
    print("\n2. Testing FindingValidator integration...")
    validated_findings = await finding_validator.validate_findings(base_findings)
    
    print(f"\nValidated Findings: {len(validated_findings)}")
    for finding in validated_findings:
        validation_mark = "✓" if finding.validation_info and finding.validation_info.get("validated", False) else "?"
        adjustment = finding.validation_info.get("confidence_adjustment", "unknown") if finding.validation_info else "unknown"
        print(f"  - {finding.title} ({finding.severity}): {finding.confidence} {validation_mark}")
        print(f"    Validation: {finding.validation_info}")
        print(f"    Confidence adjustment: {adjustment}\n")
    
    # 3. Test the full SecurityAssessmentService
    print("\n3. Testing full SecurityAssessmentService...")
    service = SecurityAssessmentService()
    
    # Create test input
    assessment_input = SecurityAssessmentInput(
        organization_name="Test Organization",
        project_name="Test Project",
        ai_provider="openai",
        scan_mode=ScanMode.COMPREHENSIVE,
        implementation_details={"process_function": VULNERABLE_CODE},
        configs={
            ConfigType.JSON_CONFIG: """
            {
                "model": "gpt-3.5-turbo",
                "temperature": 0.9,
                "max_tokens": 2000
            }
            """
        },
        architecture_description="Test architecture for a chatbot application"
    )
    
    # Run assessment
    result = await service.analyze_input(assessment_input)
    
    # Print results
    print(f"\nAssessment Results:")
    print(f"  Overall Score: {result.overall_score}/100")
    print(f"  Risk Level: {result.overall_risk_level}")
    print(f"  Vulnerabilities Found: {len(result.vulnerabilities)}")
    
    for i, vulnerability in enumerate(result.vulnerabilities):
        validation_mark = "✓" if vulnerability.validation_info and vulnerability.validation_info.get("validated", False) else "?"
        print(f"\n  {i+1}. {vulnerability.title} ({vulnerability.severity}): {vulnerability.confidence} {validation_mark}")
        print(f"     Category: {vulnerability.category}")
        print(f"     Description: {vulnerability.description[:150]}...")
        if vulnerability.validation_info:
            print(f"     Validation Score: {vulnerability.validation_info.get('validation_score', 'N/A')}")
            print(f"     Similar Vulnerability: {vulnerability.validation_info.get('similar_vulnerability', 'N/A')}")
    
    print("\n=== TEST COMPLETED ===\n")

if __name__ == "__main__":
    asyncio.run(test_new_architecture()) 