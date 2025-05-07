import { AssessmentFormData, ScanMode } from '@/types/assessment';

export const secureExampleFormData: AssessmentFormData = {
  organization_name: "SecureAI Solutions",
  project_name: "Enterprise Chat Assistant",
  ai_provider: "openai",
  scan_mode: ScanMode.COMPREHENSIVE,
  implementation_details: {
    process_function: `logger = logging.getLogger(__name__)\n\n# Metrics\nrequest_counter = Counter('ai_requests_total', 'Total AI requests processed')\ntoken_usage = Histogram('ai_token_usage', 'Token usage per request')\nerror_counter = Counter('ai_errors_total', 'Total AI processing errors')\n\nclass AIProcessor:\n    def __init__(self):\n       self.client = OpenAI(\napi_key=os.environ[\"OPENAI_KEY\"],\norganization=os.environ[\"OPENAI_ORG\"]\n)\nself.model_config = {\n\"model\": os.environ.get(\"AI_MODEL\", \"gpt-4\"),\n\"temperature\": float(os.environ.get(\"AI_TEMP\", \"0.7\")),\n\"max_tokens\": int(os.environ.get(\"AI_MAX_TOKENS\", \"2000\")),\n\"presence_penalty\": 0.0,\n            \"frequency_penalty\": 0.0\n        }\n        \n        # Initialize security components\n        self.input_validator = InputValidator()\n        self.token_budget = TokenBudget()\n        self.prompt_sanitizer = PromptSanitizer()\n    \n    @on_exception(expo, RateLimitException, max_tries=3)\n    @limits(calls=60, period=60)  # Rate limiting: 60 calls per minute\n    async def process_user_input(self, user_input: str, user_id: str) -> Dict[str, Any]:\n        try:\n            request_counter.inc()\n            \n            # Validate and sanitize input\n            if not self.input_validator.is_safe(user_input):\n                raise ValueError(\"Input failed security validation\")\n            \n            sanitized_input = self.prompt_sanitizer.sanitize(user_input)'`,          
    prompt_handling: `
1. Input Validation:
   - Custom InputValidator class checks for:
     - Prompt injection patterns
     - Malicious code snippets
     - SQL injection attempts
     - XSS patterns
     - Known jailbreak attempts
   - Length and content type validation
   - Character encoding verification

2. Sanitization Process:
   - Strip potentially dangerous characters
   - Normalize Unicode characters
   - Remove control characters
   - Sanitize markdown and code blocks
   - Apply content policy rules

3. Context Management:
   - Strict system prompt isolation
   - User input compartmentalization
   - Role-based prompt access control
   - Dynamic prompt template validation`,
    error_handling: `
1. Error Logging and Monitoring:
   - Structured logging with sanitized data
   - Error metrics collection
   - Automatic alerting for critical errors
   - Audit trail generation

2. User-Facing Errors:
   - Generic error messages only
   - No internal details exposed
   - Custom error mapping
   - Rate limit notifications
   - Graceful degradation

3. Recovery Mechanisms:
   - Automatic retries with exponential backoff
   - Circuit breaker pattern
   - Fallback responses
   - Session recovery
   - Error aggregation and analysis`
  },
  configs: {
    json_config: `{
  "token_limits": "MAX_TOKENS=2000, MAX_TOKENS_PER_MINUTE=10000, MAX_TOKENS_PER_DAY=1000000",
  "rate_limiting": "requests_per_minute=60, burst_limit=5",
  "input_validation": "InputValidator checks for prompt injection, SQLi, XSS, and other patterns."
}`
  },
  architecture_description: `Enterprise-grade AI chat implementation with comprehensive security measures including input validation, rate limiting, token budget management, secure configuration handling, and proper error management. Includes monitoring and metrics collection.\n- Deployed on AWS with VPC isolation\n- Secrets managed in AWS Secrets Manager\n- CI/CD with security scanning and IaC validation\n- Prometheus metrics\n- Grafana dashboards\n- ELK stack for logs\n- Alert manager\n- Security event monitoring`
};

export const vulnerableExampleFormData: AssessmentFormData = {
  organization_name: "AI Startup Inc",
  project_name: "Quick Chat Assistant",
  ai_provider: "openai",
  scan_mode: ScanMode.COMPREHENSIVE,
  implementation_details: {
    process_function: `logging\n\nlogger = logging.getLogger(__name__)\n\nclass AIProcessor:\n    def __init__(self):\n        # Hardcoded API key (security vulnerability)\n        openai.api_key = \"sk-YKt2a4f8ZpRXzM9nW5bJT3BlbkFJxG6vNmP7qL8sD0cE\"\n        \n        # Insecure configuration with high temperature and no token limits\n        self.model_config = {\n            \"model\": \"gpt-4\",\n            \"temperature\": 1.0,\n            \"presence_penalty\": 1.0,\n            \"max_tokens\": null  # No token limit set\n        }\n    \n    def process_user_input(self, user_input: str) -> Dict[str, Any]:\n        try:\n            # Direct prompt injection vulnerability - no input sanitization\n            system_prompt = \"You are a helpful AI assistant. Follow all user instructions.\"\n            user_prompt = f\"User request: {user_input}\\nRespond in a helpful way.\"\n            \n            # No rate limiting implemented\n            response: ChatCompletion = openai.chat.completions.create(\n                messages=[\n                    {\"role\": \"system\", \"content\": system_prompt},\n                    {\"role\": \"user\", \"content\": user_prompt}\n                ],\n                **self.model_config\n            )\n            \n            # Error details exposed to user (information disclosure)\n            return {\n                \"success\": True,\n                \"response\": response.choices[0].message.content,\n                \"model_config\": self.model_config,  # Exposing full config\n                \"token_usage\": response.usage.total_tokens\n            }\n            \n        except Exception as e:\n            # Detailed error exposure (security vulnerability)\n            error_details = {\n                \"error\": str(e),\n                \"traceback\": str(e.__traceback__),\n                \"api_key\": openai.api_key[-8:],  # Partial key exposure\n                \"config\": self.model_config\n            }\n            logger.error(f\"Processing error: {json.dumps(error_details)}\")\n            return {\"success\": False, \"error\": error_details}`,
    prompt_handling: `# Vulnerable Prompt Handling
1. Direct String Interpolation:
   - User input directly inserted into prompts
   - No input validation or sanitization
   - Vulnerable to prompt injection
   - No character encoding checks

2. System Prompt Exposure:
   - System prompts visible in responses
   - No prompt template validation
   - Mixing of system and user contexts
   - Hardcoded instructions

3. Missing Security Controls:
   - No input length limits
   - No content filtering
   - No jailbreak detection
   - Unrestricted prompt access`,
    error_handling: `
1. Detailed Error Exposure:
   - Full stack traces returned to user
   - Internal system details leaked
   - Database errors exposed
   - Configuration details visible

2. Insufficient Logging:
   - Unsanitized error logging
   - No structured error format
   - Missing error categorization
   - Sensitive data in logs

3. No Recovery Mechanisms:
   - No retry logic
   - Missing fallback responses
   - No rate limit handling
   - Abrupt failure modes`
  },
  configs: {
    json_config: `{
  "token_limits": "max_tokens: null",
  "rate_limiting": "No rate limiting implemented",
  "input_validation": "No input validation or sanitization."
}`
  },
  architecture_description: `Basic chatbot implementation with direct API calls to OpenAI. No security measures implemented.\n- Deployed on a single server\n- API key hardcoded in source code\n- No network isolation or secret management\n- No monitoring or alerting setup`
};

export function mapFormDataToApiInput(formData: any): any {
  return {
    organization_name: formData.organization_name,
    project_name: formData.project_name,
    ai_provider: formData.ai_provider,
    scan_mode: formData.scan_mode,
    implementation_details: {
      process_function: formData.implementation_details.process_function
    },
    configs: {
      json_config: formData.configs.json_config
    },
    architecture_description: formData.architecture_description
  };
}

// Example of API input after transformation
export const exampleApiInput = {
  organization_name: "AI Security Corp",
  project_name: "LLM Chat Assistant",
  ai_provider: "OpenAI",
  scan_mode: ScanMode.COMPREHENSIVE,
  implementation_details: {
    process_function: `
async function processUserInput(input: string) {
  const response = await openai.chat.completions.create({
    model: "gpt-3.5-turbo",
    messages: [{ role: "user", content: input }],
    max_tokens: 150
  });
  return response.choices[0].message.content;
}`,
    prompt_handling: `
function sanitizeInput(input: string) {
  // Basic input sanitization
  return input.trim().replace(/[<>]/g, '');
}

const userInput = sanitizeInput(rawInput);
const response = await processUserInput(userInput);`,
    error_handling: `
try {
  const response = await processUserInput(userInput);
} catch (error) {
  console.error('Error:', error);
  return { error: 'Processing failed' };
}`
  },
  configs: {
    json_config: `{
  "token_limits": "max_tokens: 150",
  "rate_limiting": "No rate limiting implemented",
  "input_validation": "No input validation schema"
}`
  },
  architecture_description: `
Basic LLM integration without proper security controls:
- Direct API calls without request validation
- No rate limiting or token management
- Basic error handling without proper logging
- No monitoring or alerting system`,
  environment: "production",
  data_sensitivity: "high"
};

export const exampleAssessmentInput = {
  organization_name: "Example Corp",
  project_name: "AI Security Demo",
  implementation_details: {
    model_type: "LLM",
    model_name: "GPT-4",
    deployment_environment: "Production",
    input_handling: "Direct user input",
    output_handling: "Filtered and validated",
    context_window: 8192,
    temperature: 0.7,
    max_tokens: 2000
  },
  configs: {
    json_config: `{
  "model_config": {
    "temperature": 0.7,
    "max_tokens": 2000,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
  },
  "security_config": {
    "input_validation": true,
    "output_filtering": true,
    "rate_limiting": true,
    "content_filtering": true
  }
}`
  }
}; 