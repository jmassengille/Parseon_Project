import asyncio
from app.services.assessment_service import SecurityAssessmentService
from app.schemas.assessment_input import SecurityAssessmentInput, ConfigType, AIProvider

async def test_basic_assessment():
    # Create test input
    test_input = SecurityAssessmentInput(
        organization_name="Test Corp",
        project_name="AI Chat Bot",
        ai_provider=AIProvider.OPENAI,
        configs={
            ConfigType.ENV_FILE: """
            OPENAI_API_KEY=sk-test123
            MODEL_NAME=gpt-3.5-turbo
            """,
            ConfigType.JSON_CONFIG: """
            {
                "temperature": 0.9,
                "presence_penalty": 0.1
            }
            """
        },
        implementation_details={
            "prompt_handling": "prompt = user_input  # No sanitization"
        },
        architecture_description="Simple API endpoint that forwards user input to OpenAI"
    )

    # Run assessment
    service = SecurityAssessmentService()
    results = await service.analyze_input(test_input)
    
    # Print findings
    print("\nSecurity Assessment Results:")
    print("============================")
    for finding in results["initial_findings"]:
        print(f"\nIssue Found:")
        print(f"Category: {finding.category}")
        print(f"Risk Level: {finding.risk_level}")
        print(f"Description: {finding.description}")
        print(f"Impact: {finding.impact}")
        print(f"Remediation: {finding.remediation}")
        if finding.code_context:
            print(f"Context: {finding.code_context}")

if __name__ == "__main__":
    asyncio.run(test_basic_assessment()) 