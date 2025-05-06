import { AssessmentFormData, SecurityAssessmentInput, ScanMode } from '@/types/assessment';

export const exampleFormData: AssessmentFormData = {
  organizationName: "AI Security Corp",
  projectName: "LLM Chat Assistant",
  aiProvider: "OpenAI",
  implementationDetails: {
    mainImplementation: `
async function processUserInput(input: string) {
  const response = await openai.chat.completions.create({
    model: "gpt-3.5-turbo",
    messages: [{ role: "user", content: input }],
    max_tokens: 150
  });
  return response.choices[0].message.content;
}`,
    promptHandling: `
function sanitizeInput(input: string) {
  // Basic input sanitization
  return input.trim().replace(/[<>]/g, '');
}

const userInput = sanitizeInput(rawInput);
const response = await processUserInput(userInput);`,
    errorHandling: `
try {
  const response = await processUserInput(userInput);
} catch (error) {
  console.error('Error:', error);
  return { error: 'Processing failed' };
}`
  },
  securityConfig: {
    tokenLimits: `
const MAX_TOKENS = 150;
const MAX_REQUESTS_PER_MINUTE = 10;

if (calculateTokens(input) > MAX_TOKENS) {
  throw new Error('Token limit exceeded');
}`,
    rateLimiting: `
const rateLimit = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 10 // limit each IP to 10 requests per windowMs
});

app.use('/api/chat', rateLimit);`,
    inputValidation: `
const inputSchema = z.object({
  message: z.string().min(1).max(500),
  context: z.string().optional()
});

const validated = inputSchema.parse(request.body);`
  },
  architecture: {
    overview: `
Our LLM Chat Assistant uses a three-tier architecture:
1. Frontend: React/Next.js web application
2. Backend: Node.js API server with rate limiting and input validation
3. AI Layer: OpenAI API integration with token management`,
    deployment: `
- Frontend deployed on Vercel
- Backend runs on AWS Lambda with API Gateway
- Environment variables stored in AWS Secrets Manager
- API keys rotated every 30 days`,
    monitoring: `
- CloudWatch metrics for API usage and errors
- Datadog for performance monitoring
- Custom logging for LLM interactions
- Alert thresholds for unusual activity patterns`
  }
};

export function mapFormDataToApiInput(formData: AssessmentFormData): SecurityAssessmentInput {
  return {
    organization_name: formData.organizationName,
    project_name: formData.projectName,
    ai_provider: formData.aiProvider,
    scan_mode: ScanMode.COMPREHENSIVE,
    implementation_details: {
      process_function: formData.implementationDetails.mainImplementation,
      prompt_handling: formData.implementationDetails.promptHandling,
      error_handling: formData.implementationDetails.errorHandling
    },
    configs: {
      token_limits: formData.securityConfig.tokenLimits,
      rate_limiting: formData.securityConfig.rateLimiting,
      input_validation: formData.securityConfig.inputValidation
    },
    architecture_description: [
      formData.architecture.overview,
      'Deployment: ' + formData.architecture.deployment,
      'Monitoring: ' + formData.architecture.monitoring
    ].join('\n\n'),
    environment: 'production',
    data_sensitivity: 'medium'
  };
}

// Example of API input after transformation
export const exampleApiInput: SecurityAssessmentInput = {
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
    token_limits: "max_tokens: 150",
    rate_limiting: "No rate limiting implemented",
    input_validation: "No input validation schema"
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

export const exampleAssessmentInput: SecurityAssessmentInput = {
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
    model_config: {
      temperature: 0.7,
      max_tokens: 2000,
      top_p: 1.0,
      frequency_penalty: 0.0,
      presence_penalty: 0.0
    },
    security_config: {
      input_validation: true,
      output_filtering: true,
      rate_limiting: true,
      content_filtering: true
    }
  }
}; 