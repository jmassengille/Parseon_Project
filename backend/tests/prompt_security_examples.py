"""
Examples of vulnerable and secure prompt handling code for AI applications.
These examples can be used for testing and improving the accuracy of the security scanner.
"""

# VULNERABLE EXAMPLES

# Example 1: Direct string interpolation (high risk of prompt injection)
VULNERABLE_EXAMPLE_1 = """
def process_user_question(user_input):
    prompt = f"Answer this question: {user_input}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']
"""

# Example 2: No input validation (moderate risk)
VULNERABLE_EXAMPLE_2 = """
def generate_response(user_prompt):
    # No validation or sanitization
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=user_prompt,
        max_tokens=500
    )
    return response.text.strip()
"""

# Example 3: Hardcoded API keys (high risk)
VULNERABLE_EXAMPLE_3 = """
openai.api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"

def get_completion(prompt):
    return openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt
    )
"""

# Example 4: System prompt mixing with user input (high risk)
VULNERABLE_EXAMPLE_4 = """
def enhanced_prompt(user_input):
    system_prompt = "You are an AI assistant that helps with coding."
    combined_prompt = system_prompt + "\\n\\n" + user_input
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=combined_prompt
    )
    return response.choices[0].text
"""

# SECURE EXAMPLES

# Example 1: Proper prompt structure and input validation
SECURE_EXAMPLE_1 = """
def process_user_question(user_input):
    # Validate input
    if not is_safe_input(user_input):
        return "Invalid or unsafe input provided."
    
    # Use proper message structure
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message['content']

def is_safe_input(text):
    # Length check
    if len(text) > 4000:
        return False
    
    # Content check
    if contains_prompt_injection_patterns(text):
        return False
    
    return True
"""

# Example 2: Environment variable for API key
SECURE_EXAMPLE_2 = """
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_completion(prompt):
    # Validate prompt
    validated_prompt = validate_prompt(prompt)
    
    return openai.Completion.create(
        model="text-davinci-003",
        prompt=validated_prompt
    )
"""

# Example 3: Role-based prompt structure
SECURE_EXAMPLE_3 = """
def get_ai_response(query):
    # Sanitize input
    query = sanitize_input(query)
    
    # Use role-based message structure
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that provides information about programming."
            },
            {
                "role": "user",
                "content": query
            }
        ]
    )
    return response.choices[0].message.content
    
def sanitize_input(text):
    # Remove potentially dangerous sequences
    text = re.sub(r'<[^>]*>', '', text)  # Remove HTML/XML tags
    return text.strip()
"""

# Example 4: Using jailbreak detection
SECURE_EXAMPLE_4 = """
def process_prompt(user_input):
    # Check for potential jailbreak attempts
    if detect_jailbreak_attempt(user_input):
        return "I cannot process this input as it appears to be attempting to bypass AI safety measures."
    
    # Rate limiting
    if not rate_limiter.allow_request(get_user_id()):
        return "Rate limit exceeded. Please try again later."
    
    # Use separate system and user prompts
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content

def detect_jailbreak_attempt(text):
    jailbreak_patterns = [
        r"ignore previous instructions",
        r"ignore all rules",
        r"pretend to be",
        r"do anything now",
        r"no ethical constraints",
        r"bypass"
    ]
    
    for pattern in jailbreak_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False
"""

# Configuration examples

VULNERABLE_CONFIG = """
{
    "model": "gpt-3.5-turbo",
    "api_key": "sk-1234567890abcdefghijklmnopqrstuvwxyz",
    "temperature": 1.5,
    "max_tokens": 10000,
    "system_prompt": "You are a helpful assistant."
}
"""

SECURE_CONFIG = """
{
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 2000,
    "frequency_penalty": 0.1,
    "presence_penalty": 0.1,
    "rate_limit": {
        "requests_per_minute": 60,
        "tokens_per_minute": 40000
    },
    "input_validation": {
        "max_length": 4000,
        "check_jailbreak_patterns": true
    },
    "token_tracking": true
}
"""

def get_examples():
    """Return dictionary of examples for testing"""
    return {
        "vulnerable": {
            "direct_interpolation": VULNERABLE_EXAMPLE_1,
            "no_validation": VULNERABLE_EXAMPLE_2,
            "hardcoded_keys": VULNERABLE_EXAMPLE_3,
            "prompt_mixing": VULNERABLE_EXAMPLE_4,
            "insecure_config": VULNERABLE_CONFIG
        },
        "secure": {
            "validated_input": SECURE_EXAMPLE_1,
            "env_variables": SECURE_EXAMPLE_2,
            "role_separation": SECURE_EXAMPLE_3,
            "jailbreak_detection": SECURE_EXAMPLE_4,
            "secure_config": SECURE_CONFIG
        }
    }

if __name__ == "__main__":
    examples = get_examples()
    print(f"Loaded {len(examples['vulnerable'])} vulnerable examples")
    print(f"Loaded {len(examples['secure'])} secure examples") 