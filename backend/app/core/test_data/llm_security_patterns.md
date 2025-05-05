# LLM Security Patterns

## Prompt Injection Defense
Technique ID: LLM-001

### Description
Implements comprehensive defenses against various forms of prompt injection attacks, including direct injection, indirect injection, and chain-of-thought manipulation.

### Examples
```python
def secure_prompt_handler(user_input: str, system_prompt: str) -> bool:
    # Validate input against known malicious patterns
    if contains_injection_patterns(user_input):
        return False
        
    # Enforce strict role boundaries
    if violates_role_boundaries(user_input, system_prompt):
        return False
        
    # Check for instruction override attempts
    if contains_override_attempts(user_input):
        return False
        
    return True
```

### Mitigation
- Input sanitization and validation
- Role-based prompt boundaries
- System prompt protection
- Instruction set validation
- Output verification

### References
- OWASP LLM Top 10
- Microsoft LLM Security Guidelines

## Output Sanitization
Technique ID: LLM-002

### Description
Prevents sensitive data leakage and ensures output compliance with security policies.

### Examples
```python
def sanitize_llm_output(response: str, security_policy: Dict) -> str:
    # Remove potential PII
    response = remove_pii(response)
    
    # Check against allowed content policies
    if not complies_with_policy(response, security_policy):
        return generate_policy_violation_response()
        
    # Validate output structure
    return validate_output_structure(response)
```

### Mitigation
- PII detection and removal
- Content policy enforcement
- Output structure validation
- Response templating

### References
- Data Privacy Framework
- LLM Output Security Guidelines

## Rate Limiting and Quota Management
Technique ID: LLM-003

### Description
Prevents abuse through systematic query patterns and ensures fair resource allocation.

### Examples
```python
@rate_limit(max_requests=100, window_seconds=3600)
@quota_check(user_id, quota_type="tokens")
async def handle_llm_request(prompt: str, user_id: str):
    if await is_suspicious_pattern(user_id, prompt):
        raise SecurityException("Suspicious query pattern detected")
    return await process_llm_request(prompt)
```

### Mitigation
- Request rate limiting
- Token quota management
- Pattern-based abuse detection
- Resource allocation controls

### References
- API Security Best Practices
- LLM Rate Limiting Patterns 