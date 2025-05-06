export type FormSection = 'project_name' | 'ai_provider' | 'code_snippets' | 'security_config' | 'architecture';
export type CodeSnippetField = 'main_implementation' | 'prompt_handling' | 'error_handling';
export type SecurityConfigField = 'token_limits' | 'rate_limiting' | 'input_validation';
export type ArchitectureField = 'overview' | 'deployment' | 'monitoring';

export enum ScanMode {
  COMPREHENSIVE = 'COMPREHENSIVE',
  PROMPT_SECURITY = 'PROMPT_SECURITY',
  API_SECURITY = 'API_SECURITY'
}

export interface AssessmentFormData {
  organizationName: string;
  projectName: string;
  aiProvider: string;
  implementationDetails: {
    mainImplementation: string;
    promptHandling: string;
    errorHandling: string;
  };
  securityConfig: {
    tokenLimits: string;
    rateLimiting: string;
    inputValidation: string;
  };
  architecture: {
    overview: string;
    deployment: string;
    monitoring: string;
  };
  use_mock_data?: boolean;
}

// API Input type for backend communication - removed to avoid confusion
// Define locally in components instead

export interface ValidationInfo {
  validation_score: number;
  similar_vulnerability: string;
  validated: boolean;
  confidence_adjustment: 'boosted' | 'reduced' | 'unchanged';
}

export interface Finding {
  id: string;
  category: string;
  severity: string;
  title: string;
  description: string;
  code_snippets: string[];
  recommendation: string;
  confidence: number;
  validation_info?: ValidationInfo;
}

export interface CategoryScore {
  score: number;
  findings: string[];
  recommendations: string[];
}

export interface AssessmentResult {
  organization_name: string;
  project_name: string;
  timestamp: string;
  overall_score: number;
  overall_risk_level: string;
  vulnerabilities: Finding[];
  priority_actions: string[];
  category_scores: {
    API_SECURITY: CategoryScore;
    PROMPT_SECURITY: CategoryScore;
    CONFIGURATION: CategoryScore;
    ERROR_HANDLING: CategoryScore;
  };
  ai_model_used: string;
  token_usage: {
    prompt_tokens: number;
    completion_tokens: number;
  };
}

// Alias for backward compatibility
export type SecurityAssessmentResult = AssessmentResult; 