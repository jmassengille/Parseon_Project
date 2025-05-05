import asyncio
from datetime import datetime
from app.schemas.assessment_input import SecurityAssessmentInput, ConfigType, AIProvider
from app.schemas.assessment_output import SecurityAssessmentResult, SecurityScore, RiskLevel
from app.services.assessment_service import SecurityAssessmentService

async def test_comprehensive_assessment():
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
                "presence_penalty": 0.1,
                "frequency_penalty": 0.1
            }
            """,
            ConfigType.CODE_SNIPPET: """
            def process_prompt(user_input):
                # No input validation
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": user_input}]
                )
                return response.choices[0].message['content']
            """
        },
        implementation_details={
            "prompt_handling": "Direct forwarding of user input without sanitization",
            "error_handling": "Basic try-except block with no specific error types"
        },
        architecture_description="REST API endpoint that receives user input and forwards to OpenAI API"
    )

    # Run assessment
    service = SecurityAssessmentService()
    initial_results = await service.analyze_input(test_input)
    
    # Create comprehensive result
    result = SecurityAssessmentResult(
        organization_name=test_input.organization_name,
        project_name=test_input.project_name,
        timestamp=datetime.utcnow(),
        prompt_security_score=SecurityScore(
            score=65.0,
            findings=["No input validation", "High temperature setting"],
            recommendations=["Implement input sanitization", "Lower temperature value"]
        ),
        api_security_score=SecurityScore(
            score=45.0,
            findings=["Exposed API key", "No rate limiting"],
            recommendations=["Use secret management", "Implement rate limiting"]
        ),
        overall_risk_level=RiskLevel.HIGH,
        vulnerabilities=initial_results["initial_findings"],
        key_findings=[
            "Multiple security controls missing",
            "High risk of prompt injection",
            "Potential for excessive API usage"
        ],
        priority_actions=[
            "1. Implement proper API key management",
            "2. Add input validation and sanitization",
            "3. Set up rate limiting"
        ],
        model_used="gpt-3.5-turbo",
        token_usage={"prompt_tokens": 0, "completion_tokens": 0}
    )
    
    # Print comprehensive results
    print("\nComprehensive Security Assessment Results:")
    print("=========================================")
    print(f"\nOrganization: {result.organization_name}")
    print(f"Project: {result.project_name}")
    print(f"Overall Risk Level: {result.overall_risk_level}")
    
    print("\nScores:")
    print(f"Prompt Security: {result.prompt_security_score.score}")
    print(f"API Security: {result.api_security_score.score}")
    
    print("\nKey Findings:")
    for finding in result.key_findings:
        print(f"- {finding}")
    
    print("\nPriority Actions:")
    for action in result.priority_actions:
        print(f"- {action}")
    
    print("\nDetailed Vulnerabilities:")
    for vuln in result.vulnerabilities:
        print(f"\nIssue Found:")
        print(f"Category: {vuln.category}")
        print(f"Risk Level: {vuln.risk_level}")
        print(f"Description: {vuln.description}")
        print(f"Impact: {vuln.impact}")
        print(f"Remediation: {vuln.remediation}")
        if vuln.code_context:
            print(f"Context: {vuln.code_context}")

if __name__ == "__main__":
    asyncio.run(test_comprehensive_assessment()) 