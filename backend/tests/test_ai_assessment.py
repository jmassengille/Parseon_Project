import asyncio
from app.schemas.assessment_input import SecurityAssessmentInput, ConfigType, AIProvider
from app.schemas.assessment import VulnerabilityFinding, RiskLevel
from app.services.assessment_service import SecurityAssessmentService

async def test_ai_assessment():
    print("Starting AI Security Assessment...")
    
    # Create test input with some common security issues
    test_input = SecurityAssessmentInput(
        organization_name="Test Corp",
        project_name="Customer Service AI Bot",
        ai_provider=AIProvider.OPENAI,
        configs={
            ConfigType.ENV_FILE: """
            OPENAI_API_KEY=sk-test123456789
            MODEL_NAME=gpt-3.5-turbo
            MAX_REQUESTS=None
            """,
            ConfigType.JSON_CONFIG: """
            {
                "temperature": 0.9,
                "max_tokens": null,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
            """,
            ConfigType.CODE_SNIPPET: """
            def process_user_input(user_message):
                # Direct prompt forwarding without sanitization
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.9
                )
                
                try:
                    return response.choices[0].message['content']
                except Exception as e:
                    print(f"Error: {e}")
                    return "An error occurred"
            """
        },
        implementation_details={
            "prompt_handling": "User input is passed directly to the API without validation",
            "error_handling": "Basic try-except block with generic error message",
            "rate_limiting": "No rate limiting implemented",
            "input_validation": "No input validation or sanitization"
        },
        architecture_description="""
        Simple REST API that:
        1. Accepts user input via POST request
        2. Forwards input directly to OpenAI API
        3. Returns response to user
        No middleware, no rate limiting, no input validation.
        Using basic error handling with generic error messages.
        API keys stored in environment variables.
        """
    )

    try:
        # Run assessment with GPT-3.5
        service = SecurityAssessmentService(use_gpt4=False)
        print("Running AI analysis...")
        result = await service.analyze_input(test_input)
        
        # Print results
        print("\nAI Security Assessment Results")
        print("=============================")
        print(f"\nOrganization: {result.organization_name}")
        print(f"Project: {result.project_name}")
        print(f"Model Used: {result.model_used}")
        print(f"\nOverall Score: {result.overall_score:.1f}/100")
        print(f"Overall Risk Level: {result.overall_risk_level}")
        print(f"Token Usage: {result.token_usage}")
        
        print("\nCategory Scores:")
        for category, score in result.category_scores.items():
            print(f"\n{category.replace('_', ' ').title()}:")
            print(f"Score: {score.score:.1f}/100")
            print("Key Findings:")
            for finding in score.findings:
                print(f"- {finding}")
        
        # Comment out Priority Actions section
        # print("\nPriority Actions:")
        # for i, action in enumerate(result.priority_actions, 1):
        #     print(f"{i}. {action}")
        
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

    except Exception as e:
        print(f"Error during assessment: {str(e)}")
        raise e

if __name__ == "__main__":
    asyncio.run(test_ai_assessment()) 