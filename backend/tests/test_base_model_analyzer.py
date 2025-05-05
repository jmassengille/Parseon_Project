"""
Test to evaluate the base model's ability to produce structured JSON output for AI security analysis.

This test compares the base model's capabilities when prompted with the identical prompt 
used by Parseon's AISecurityAnalyzer.
"""

import asyncio
import os
import sys
import pytest
import json
import re
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Fix import path to properly locate the app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.base_model_analyzer import BaseModelAnalyzer
from app.schemas.assessment import VulnerabilityFinding, SecurityCategory, RiskLevel
from app.core.finding_validator import FindingValidator

# Load environment variables
load_dotenv()

# Example vulnerable code with prompt injection risk
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

# Example code with database-sourced indirect prompt injection
INDIRECT_INJECTION_CODE = """
def process_user_request(user_id):
    # Load user data from database
    user_data = database.get_user_data(user_id)
    user_preferences = user_data.get("preferences", "")
    user_history = user_data.get("chat_history", [])
    
    # Create enhanced prompt with user data
    # Vulnerable because user_preferences and user_history come from database
    # without sanitization and could contain injected content from previous interactions
    enhanced_prompt = f\"\"\"
    Answer the following question based on user preferences and history:
    
    User Preferences: {user_preferences}
    
    Chat History:
    {user_history}
    
    Please provide a personalized response.
    \"\"\"
    
    # Make API call
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": enhanced_prompt}
        ]
    )
    
    return response.choices[0].message["content"]
"""

async def analyze_with_base_model_exact_prompt(code, context):
    """
    Analyze code using the base model with the EXACT SAME prompt as AISecurityAnalyzer
    """
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Use the exact same system prompt as in AISecurityAnalyzer
    system_prompt = """You are an AI security expert specializing in identifying security issues in AI-integrated applications.
    Analyze the code for potential security vulnerabilities, focusing ONLY on AI-specific security issues.
    Focus areas:
    - Prompt injection vulnerabilities
    - Insecure model loading
    - Insecure API key management
    - Insufficient input validation for AI components
    - AI-specific data leakage
    - Missing authorization for AI operations
    - Improper error handling for AI components
    - AI configuration vulnerabilities
    
    Respond with a JSON array of findings. Each finding should include:
    - "title": Brief title of the vulnerability
    - "description": Detailed description of the vulnerability
    - "severity": Either "CRITICAL", "HIGH", "MEDIUM", or "LOW"
    - "category": One of "API_SECURITY", "PROMPT_SECURITY", "CONFIGURATION", "ERROR_HANDLING"
    - "code_snippet": The relevant code where the vulnerability is found
    - "recommendation": Specific remediation steps
    - "confidence": A value between 0 and 1 indicating confidence level
    
    IMPORTANT: Only report actual AI security vulnerabilities. Do not flag proper security practices as vulnerabilities.
    If the code properly handles security (using sanitization, validation, environment variables, etc.), do not report it as vulnerable.
    If no AI-specific security issues are found, return an empty array (just "[]") without any narrative.
    
    Response format must always be valid JSON (either a populated array or an empty array "[]").
    """
    
    # Use the exact same user prompt as in AISecurityAnalyzer
    user_prompt = f"""Analyze the following code for AI security vulnerabilities:
    
    ```
    {code}
    ```
    
    Context: {context}
    """
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        
        response_text = response.choices[0].message.content
        print("Raw Response:")
        print(response_text)
        
        # Try to parse the JSON
        try:
            # Fix JSON formatting if needed
            if not response_text.strip().startswith('['):
                # Try to find a JSON array in the response
                json_match = re.search(r'(\[.*\])', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
                else:
                    # Handle common cases where the model explains first
                    if "no" in response_text.lower() and ("issue" in response_text.lower() or "vulnerabilit" in response_text.lower()):
                        print("No vulnerabilities detected by the model.")
                        return []
                    # If nothing else works, return unparsed
                    print("Could not extract JSON from response.")
                    return []
            
            # Try to parse
            findings_data = json.loads(response_text)
            
            # Convert to findings
            findings = []
            for i, finding_data in enumerate(findings_data):
                finding = {
                    "id": f"finding_{i+1}",
                    "title": finding_data.get("title", "Unnamed Finding"),
                    "description": finding_data.get("description", "No description provided"),
                    "severity": finding_data.get("severity", "MEDIUM"),
                    "category": finding_data.get("category", "PROMPT_SECURITY"),
                    "code_snippets": [finding_data.get("code_snippet", "No code snippet provided")],
                    "recommendation": finding_data.get("recommendation", "No recommendation provided"),
                    "confidence": float(finding_data.get("confidence", 0.5))
                }
                findings.append(finding)
                
            return findings
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {response_text}")
            return []
        except Exception as e:
            print(f"Error processing findings: {e}")
            return []
            
    except Exception as e:
        print(f"Error in Base Model analysis: {e}")
        return []

async def run_analyzer_test():
    """Run the comparison test"""
    print("\n=== TESTING BASE MODEL WITH EXACT PROMPT VS. AI ANALYZER ===\n")
    
    test_cases = {
        "direct_prompt_injection": VULNERABLE_CODE,
        "indirect_prompt_injection": INDIRECT_INJECTION_CODE
    }
    
    ai_analyzer = BaseModelAnalyzer()
    
    for case_name, code in test_cases.items():
        print(f"\n\n{'='*20} ANALYZING {case_name.upper()} {'='*20}\n")
        
        # 1. Analyze with existing AI analyzer
        print("\n=== EXISTING AI ANALYZER RESULTS ===\n")
        existing_findings = await ai_analyzer.analyze_code(code, case_name)
        
        if existing_findings:
            print(f"Found {len(existing_findings)} issues:")
            for finding in existing_findings:
                print(f"  - {finding.title} ({finding.severity}): {finding.confidence}")
                print(f"    {finding.description[:150]}...\n")
                print(f"    Recommendation: {finding.recommendation[:150]}...\n")
        else:
            print("No issues found.")
        
        # 2. Analyze with base model using the EXACT SAME prompt
        print("\n=== BASE MODEL WITH EXACT SAME PROMPT ===\n")
        structured_findings = await analyze_with_base_model_exact_prompt(code, case_name)
        
        if structured_findings:
            print(f"Found {len(structured_findings)} issues:")
            for finding in structured_findings:
                print(f"  - {finding['title']} ({finding['severity']}): {finding['confidence']}")
                print(f"    {finding['description'][:150]}...\n")
                print(f"    Recommendation: {finding['recommendation'][:150]}...\n")
        else:
            print("No issues found.")
        
        print("\n" + "="*80 + "\n")

# Test cases for prompt injection
PROMPT_INJECTION_CASES = [
    {
        "name": "direct_injection",
        "code": """
def process_prompt(user_input):
    # Directly use user input in the prompt
    prompt = f"Answer this question: {user_input}"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                 {"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
"""
    },
    {
        "name": "indirect_injection",
        "code": """
def search_and_respond(query):
    # Store query in database without validation
    db.store_query(query)
    
    # Later, retrieve and use in prompt
    stored_queries = db.get_recent_queries(5)
    
    for q in stored_queries:
        prompt = f"Previous query: {q}\\nAnswer this question: {query}"
        # Send to model...
"""
    }
]

# Test cases for secure patterns
SECURE_CASES = [
    {
        "name": "sanitized_input",
        "code": """
def process_prompt(user_input):
    # Sanitize user input
    sanitized = sanitize_input(user_input)
    
    # Use sanitized input in prompt
    prompt = f"Answer this question: {sanitized}"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                 {"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def sanitize_input(text):
    # Remove potential prompt injection triggers
    banned_patterns = ["ignore previous instructions", "system prompt", "as an AI language model"]
    
    for pattern in banned_patterns:
        if pattern.lower() in text.lower():
            return "Input contains disallowed content"
    
    # Apply other sanitization
    return text.strip()
"""
    }
]

# Test cases for API security
API_SECURITY_CASES = [
    {
        "name": "hardcoded_api_key",
        "code": """
def get_completion(prompt):
    # Hardcoded API key - security vulnerability
    api_key = "sk-1234567890abcdef1234567890abcdef"
    
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
"""
    },
    {
        "name": "secure_api_key",
        "code": """
def get_completion(prompt):
    # Load API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("API key not found")
    
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
"""
    }
]

@pytest.mark.asyncio
async def test_prompt_injection_detection():
    """Test that the analyzer correctly identifies prompt injection vulnerabilities"""
    analyzer = BaseModelAnalyzer()
    
    for case in PROMPT_INJECTION_CASES:
        print(f"\nTesting case: {case['name']}")
        findings = await analyzer.analyze_code(case["code"], case["name"])
        
        # Check if prompt injection was found
        found_injection = False
        for finding in findings:
            if "prompt" in finding.title.lower() and "injection" in finding.title.lower():
                found_injection = True
                assert finding.severity in ["HIGH", "CRITICAL"], f"Expected HIGH or CRITICAL severity for prompt injection, got {finding.severity}"
                print(f"Found prompt injection: {finding.title} ({finding.severity})")
                break
                
        assert found_injection, f"Failed to detect prompt injection in case: {case['name']}"

@pytest.mark.asyncio
async def test_secure_code_detection():
    """Test that the analyzer correctly identifies secure code patterns"""
    analyzer = BaseModelAnalyzer()
    
    for case in SECURE_CASES:
        print(f"\nTesting secure case: {case['name']}")
        findings = await analyzer.analyze_code(case["code"], case["name"])
        
        # For secure code, we expect no critical findings
        critical_findings = [f for f in findings if f.severity in ["CRITICAL", "HIGH"]]
        
        assert len(critical_findings) == 0, f"Found {len(critical_findings)} critical/high findings in secure code: {case['name']}"
        print(f"Correctly found no critical issues in secure code: {case['name']}")

@pytest.mark.asyncio
async def test_api_security_detection():
    """Test that the analyzer correctly identifies API security issues"""
    analyzer = BaseModelAnalyzer()
    
    # Test insecure case
    case = API_SECURITY_CASES[0]  # hardcoded API key
    print(f"\nTesting API security case: {case['name']}")
    findings = await analyzer.analyze_code(case["code"], case["name"])
    
    # Check for API key finding
    found_api_key_issue = False
    for finding in findings:
        if "api key" in finding.title.lower() or "hardcoded" in finding.title.lower():
            found_api_key_issue = True
            assert finding.severity in ["HIGH", "CRITICAL"], f"Expected HIGH or CRITICAL severity for API key issue, got {finding.severity}"
            print(f"Found API key issue: {finding.title} ({finding.severity})")
            break
            
    assert found_api_key_issue, f"Failed to detect API key issue in case: {case['name']}"
    
    # Test secure case
    case = API_SECURITY_CASES[1]  # secure API key
    findings = await analyzer.analyze_code(case["code"], case["name"])
    
    # For secure code, we expect no critical API key findings
    api_key_findings = [f for f in findings if ("api key" in f.title.lower() or "hardcoded" in f.title.lower()) and f.severity in ["CRITICAL", "HIGH"]]
    
    assert len(api_key_findings) == 0, f"Found {len(api_key_findings)} critical API key findings in secure code: {case['name']}"
    print(f"Correctly found no critical API key issues in secure code: {case['name']}")

@pytest.mark.asyncio
async def test_comparison_with_previous_results():
    """Test that the BaseModelAnalyzer produces comparable results to previous implementation"""
    # This is a placeholder test comparing with pre-existing results
    # We're just checking that the analyzer can find the same types of issues
    analyzer = BaseModelAnalyzer()
    validator = FindingValidator()
    await validator.initialize()
    
    case = PROMPT_INJECTION_CASES[0]  # direct injection
    code = case["code"]
    case_name = case["name"]
    
    # Analyze with base model analyzer
    findings = await analyzer.analyze_code(code, case_name)
    validated_findings = await validator.validate_findings(findings)
    
    # In a real implementation, we'd compare with expected findings
    # For now, just check that we get some findings
    assert len(findings) > 0, f"Expected at least one finding for {case_name}"
    
    # Check that validation works
    assert len(validated_findings) == len(findings), "Validation should not change the number of findings"
    
    # Check that at least one finding is validated (high similarity)
    has_valid_finding = False
    for finding in validated_findings:
        if finding.validation_info and finding.validation_info.get("validated", False):
            has_valid_finding = True
            break
    
    assert has_valid_finding, "Expected at least one validated finding"

if __name__ == "__main__":
    asyncio.run(run_analyzer_test())
    asyncio.run(test_prompt_injection_detection())
    asyncio.run(test_secure_code_detection())
    asyncio.run(test_api_security_detection())
    asyncio.run(test_comparison_with_previous_results()) 