export type FormSection = 'project_name' | 'ai_provider' | 'code_snippets' | 'security_config' | 'architecture';
export type CodeSnippetField = 'main_implementation' | 'prompt_handling' | 'error_handling';
export type SecurityConfigField = 'token_limits' | 'rate_limiting' | 'input_validation';
export type ArchitectureField = 'overview' | 'deployment' | 'monitoring';

export enum ScanMode {
  COMPREHENSIVE = "COMPREHENSIVE",
  PROMPT_SECURITY = "PROMPT_SECURITY",
  API_SECURITY = "API_SECURITY"
}

export enum RiskLevel {
  CRITICAL = "CRITICAL",
  HIGH = "HIGH",
  MEDIUM = "MEDIUM",
  LOW = "LOW"
}

export interface SecurityScore {
  score: number;
  findings: string[];
  recommendations: string[];
}

export interface VulnerabilityFinding {
  id: string;
  title: string;
  description: string;
  severity: string;
  category: string;
  code_snippets: string[];
  recommendation: string;
  confidence: number;
  validation_info?: Record<string, any>;
  validated: boolean;
}

export interface AssessmentFormData {
  organization_name: string;
  project_name: string;
  ai_provider: string;
  scan_mode: ScanMode;
  configs?: {
    env_file?: string;
    json_config?: string;
    code_snippet?: string;
  };
  implementation_details?: {
    prompt_handling?: string;
    error_handling?: string;
    process_function?: string;
  };
  architecture_description?: string;
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
  id?: number;
  organization_name: string;
  project_name: string;
  timestamp: string;
  overall_score: number;
  overall_risk_level: RiskLevel;
  category_scores: Record<string, SecurityScore>;
  vulnerabilities: VulnerabilityFinding[];
  priority_actions: string[];
  ai_model_used: string;
  token_usage: {
    prompt_tokens: number;
    completion_tokens: number;
  };
  environment?: string;
  data_sensitivity?: string;
  grounding_info?: Record<string, any>;
}

// Alias for backward compatibility
export type SecurityAssessmentResult = AssessmentResult; 