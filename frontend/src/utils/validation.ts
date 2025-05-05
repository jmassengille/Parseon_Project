import { z } from 'zod';
import { AssessmentFormData } from '@/types/assessment';

// Basic information validation
export const basicInfoSchema = z.object({
  project_name: z.string()
    .min(3, 'Project name must be at least 3 characters')
    .max(100, 'Project name must be less than 100 characters')
    .regex(/^[a-zA-Z0-9\s-_]+$/, 'Project name can only contain letters, numbers, spaces, hyphens, and underscores'),
  ai_provider: z.enum(['openai', 'anthropic', 'google', 'azure', 'other'], {
    required_error: 'Please select an AI provider'
  })
});

// Code snippets validation
export const codeSnippetsSchema = z.object({
  main_implementation: z.string()
    .min(50, 'Main implementation must be at least 50 characters')
    .max(5000, 'Main implementation must be less than 5000 characters'),
  prompt_handling: z.string()
    .min(50, 'Prompt handling must be at least 50 characters')
    .max(5000, 'Prompt handling must be less than 5000 characters'),
  error_handling: z.string()
    .min(50, 'Error handling must be at least 50 characters')
    .max(5000, 'Error handling must be less than 5000 characters')
});

// Security configuration validation
export const securityConfigSchema = z.object({
  token_limits: z.string()
    .min(20, 'Token limits description must be at least 20 characters')
    .max(1000, 'Token limits description must be less than 1000 characters')
    .refine((val) => {
      // Check for common token limit patterns
      const hasNumber = /\d+/.test(val);
      const hasUnit = /(token|request|minute|hour|day)/i.test(val);
      return hasNumber && hasUnit;
    }, 'Must include specific token limits and units'),
  rate_limiting: z.string()
    .min(20, 'Rate limiting description must be at least 20 characters')
    .max(1000, 'Rate limiting description must be less than 1000 characters')
    .refine((val) => {
      // Check for rate limiting patterns
      const hasNumber = /\d+/.test(val);
      const hasTimeUnit = /(second|minute|hour|day)/i.test(val);
      return hasNumber && hasTimeUnit;
    }, 'Must include specific rate limits and time units'),
  input_validation: z.string()
    .min(20, 'Input validation description must be at least 20 characters')
    .max(1000, 'Input validation description must be less than 1000 characters')
});

// Architecture validation
export const architectureSchema = z.object({
  overview: z.string()
    .min(50, 'Architecture overview must be at least 50 characters')
    .max(2000, 'Architecture overview must be less than 2000 characters'),
  deployment: z.string()
    .min(50, 'Deployment description must be at least 50 characters')
    .max(2000, 'Deployment description must be less than 2000 characters'),
  monitoring: z.string()
    .min(50, 'Monitoring description must be at least 50 characters')
    .max(2000, 'Monitoring description must be less than 2000 characters')
});

// Complete form validation schema
export const assessmentFormSchema = z.object({
  project_name: basicInfoSchema.shape.project_name,
  ai_provider: basicInfoSchema.shape.ai_provider,
  code_snippets: codeSnippetsSchema,
  security_config: securityConfigSchema,
  architecture: architectureSchema
});

// Validation helper functions
export const validateField = async <T>(
  schema: z.ZodType<T>,
  value: T,
  fieldName: string
): Promise<{ isValid: boolean; error?: string }> => {
  try {
    await schema.parseAsync(value);
    return { isValid: true };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        isValid: false,
        error: error.errors[0].message
      };
    }
    return {
      isValid: false,
      error: `Invalid ${fieldName}`
    };
  }
};

// Real-time validation for code snippets
export const validateCodeSnippet = (code: string): { isValid: boolean; error?: string } => {
  // Basic syntax validation
  const hasBrackets = /[{}]/.test(code);
  const hasParentheses = /[()]/.test(code);
  const hasSemicolon = /;/.test(code);
  
  if (!hasBrackets || !hasParentheses || !hasSemicolon) {
    return {
      isValid: false,
      error: 'Code snippet appears to be incomplete or invalid'
    };
  }
  
  return { isValid: true };
};

// Security configuration validation
export const validateSecurityConfig = (config: string): { isValid: boolean; error?: string } => {
  const hasNumbers = /\d+/.test(config);
  const hasSecurityTerms = /(limit|restrict|validate|sanitize|encrypt|secure)/i.test(config);
  
  if (!hasNumbers || !hasSecurityTerms) {
    return {
      isValid: false,
      error: 'Security configuration must include specific limits and security measures'
    };
  }
  
  return { isValid: true };
}; 