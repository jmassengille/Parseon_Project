"use client";

import React, { useState } from "react";
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography,
  Paper,
  Tooltip,
  IconButton,
  Alert,
  CircularProgress,
  Theme,
  Grid,
  FormHelperText,
  Card,
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Divider,
} from "@mui/material";
import InfoIcon from "@mui/icons-material/Info";
import SecurityIcon from "@mui/icons-material/Security";
import CodeIcon from "@mui/icons-material/Code";
import ArchitectureIcon from "@mui/icons-material/Architecture";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import VisibilityIcon from "@mui/icons-material/Visibility";
import { styled } from "@mui/material/styles";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

const steps = [
  "Basic Info",
  "Code & Config",
  "Security Settings",
  "Architecture"
];

const StyledPaper = styled(Paper)(({ theme }: { theme: Theme }) => ({
  padding: theme.spacing(4),
  backgroundColor: theme.palette.background.paper,
  maxWidth: "1000px",
  margin: "0 auto",
  borderRadius: theme.shape.borderRadius * 2,
  boxShadow: theme.shadows[2],
  color: theme.palette.text.primary,
}));

const StyledHeader = styled(Typography)({
  fontWeight: 700,
  color: "#1a1a1a",
  fontSize: "1.5rem",
  letterSpacing: "-0.5px",
  margin: 0,
  padding: 0,
  lineHeight: 1.2,
});

const StyledDialog = styled(Dialog)(({ theme }: { theme: Theme }) => ({
  "& .MuiDialog-paper": {
    minWidth: "800px",
    maxWidth: "90vw",
    maxHeight: "90vh",
    backgroundColor: theme.palette.background.paper,
    color: theme.palette.text.primary,
  },
}));

const StyledTabPanel = styled(Box)(({ theme }: { theme: Theme }) => ({
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.default,
  borderRadius: theme.shape.borderRadius,
  marginTop: theme.spacing(2),
  color: theme.palette.text.primary,
}));

const tooltips = {
  project: "Name of your AI project",
  provider: "The AI service provider you're using",
  mainImplementation: "Main code that handles AI requests and responses",
  promptHandling: "Code that processes, validates, and sanitizes prompts",
  errorHandling: "Error handling, logging, and fallback mechanisms",
  tokenLimits: "Token limits, context windows, and usage restrictions",
  rateLimiting: "Rate limiting and request throttling implementation",
  inputValidation: "Input validation, sanitization, and security checks",
  architecture: "High-level architecture of your AI implementation",
  deployment: "Deployment environment and security measures",
  monitoring: "Monitoring, logging, and alerting setup"
} as const;

const exampleData = {
  organizationName: "TechSecure Solutions",
  projectName: "AI Customer Support Assistant",
  aiProvider: "openai",
  implementationDetails: {
    mainImplementation: 
`// AI Request Handler with Security Controls
import { OpenAI } from 'openai';
import { RateLimiter } from './security/rate-limiter';
import { PromptValidator } from './security/prompt-validator';
import { TokenManager } from './security/token-manager';
import { SecurityLogger } from './utils/security-logger';

class AIRequestHandler {
  private openai: OpenAI;
  private rateLimiter: RateLimiter;
  private promptValidator: PromptValidator;
  private tokenManager: TokenManager;
  private logger: SecurityLogger;

  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
      organization: process.env.OPENAI_ORG_ID,
    });
    this.rateLimiter = new RateLimiter();
    this.promptValidator = new PromptValidator();
    this.tokenManager = new TokenManager();
    this.logger = new SecurityLogger();
  }

  async processRequest(userId: string, prompt: string): Promise<AIResponse> {
    try {
      // Rate limiting check
      await this.rateLimiter.checkLimit(userId);

      // Validate and sanitize prompt
      const sanitizedPrompt = await this.promptValidator.validateAndSanitize(prompt);

      // Check token budget
      await this.tokenManager.checkAndReserveTokens(userId, sanitizedPrompt);

      // Log request attempt
      await this.logger.logRequest({
        userId,
        promptLength: prompt.length,
        timestamp: new Date(),
        requestType: 'customer-support'
      });

      // Process with OpenAI
      const response = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          { 
            role: "system", 
            content: "You are a secure customer support assistant. Never reveal sensitive information."
          },
          { role: "user", content: sanitizedPrompt }
        ],
        max_tokens: this.tokenManager.getMaxTokens(),
        temperature: 0.7,
        presence_penalty: 0.6,
        frequency_penalty: 0.5,
      });

      // Log successful completion
      await this.logger.logCompletion({
        userId,
        tokensUsed: response.usage?.total_tokens || 0,
        timestamp: new Date()
      });

      return {
        content: response.choices[0].message.content,
        usage: response.usage,
        metadata: {
          model: response.model,
          timestamp: new Date(),
        }
      };
    } catch (error) {
      await this.handleError(error, userId);
      throw error;
    }
  }
}`,
    promptHandling: 
`// Prompt Security Handler
import { createHash } from 'crypto';
import { PromptSecurityConfig } from '../config/security';
import { SecurityLogger } from '../utils/security-logger';
import { BlockList } from '../security/block-list';

export class PromptValidator {
  private blockList: BlockList;
  private logger: SecurityLogger;
  private config: PromptSecurityConfig;

  constructor() {
    this.blockList = new BlockList();
    this.logger = new SecurityLogger();
    this.config = new PromptSecurityConfig();
  }

  async validateAndSanitize(prompt: string): Promise<string> {
    // Generate prompt hash for tracking
    const promptHash = this.generatePromptHash(prompt);
    
    // Check prompt length
    if (prompt.length > this.config.maxPromptLength) {
      throw new Error('Prompt exceeds maximum length');
    }

    // Check for blocked patterns
    const blockedPattern = await this.blockList.findMatch(prompt);
    if (blockedPattern) {
      await this.logger.logSecurityEvent({
        type: 'BLOCKED_PATTERN_DETECTED',
        pattern: blockedPattern,
        promptHash,
        timestamp: new Date()
      });
      throw new Error('Potentially unsafe prompt detected');
    }

    // Check for prompt injection attempts
    if (this.detectPromptInjection(prompt)) {
      await this.logger.logSecurityEvent({
        type: 'PROMPT_INJECTION_ATTEMPT',
        promptHash,
        timestamp: new Date()
      });
      throw new Error('Potential prompt injection detected');
    }

    // Sanitize prompt
    let sanitized = prompt;
    
    // Remove potential HTML/JS
    sanitized = sanitized.replace(/<[^>]*>/g, '');
    
    // Remove potential SQL injection patterns
    sanitized = sanitized.replace(/['";\\\%]/g, '');
    
    // Remove control characters
    sanitized = sanitized.replace(/[\\x00-\\x1F\\x7F-\\x9F]/g, '');

    // Normalize whitespace
    sanitized = sanitized.replace(/\\s+/g, ' ').trim();

    // Log sanitization result
    await this.logger.logPromptSanitization({
      originalLength: prompt.length,
      sanitizedLength: sanitized.length,
      promptHash,
      timestamp: new Date()
    });

    return sanitized;
  }

  private generatePromptHash(prompt: string): string {
    return createHash('sha256').update(prompt).digest('hex');
  }

  private detectPromptInjection(prompt: string): boolean {
    const injectionPatterns = [
      /ignore previous instructions/i,
      /ignore above instructions/i,
      /disregard previous commands/i,
      /bypass security/i,
      /override security/i,
      /ignore rules/i
    ];

    return injectionPatterns.some(pattern => pattern.test(prompt));
  }
}`,
    errorHandling: 
`// Error Handler with Security Logging
import { ErrorReporter } from '../monitoring/error-reporter';
import { SecurityLogger } from '../utils/security-logger';
import { NotificationService } from '../services/notification';
import { ErrorClassifier } from '../security/error-classifier';

export class AIErrorHandler {
  private errorReporter: ErrorReporter;
  private logger: SecurityLogger;
  private notifier: NotificationService;
  private classifier: ErrorClassifier;

  constructor() {
    this.errorReporter = new ErrorReporter();
    this.logger = new SecurityLogger();
    this.notifier = new NotificationService();
    this.classifier = new ErrorClassifier();
  }

  async handleError(error: Error, context: RequestContext): Promise<void> {
    try {
      // Classify the error
      const classification = this.classifier.classify(error);
      
      // Log the error with security context
      await this.logger.logError({
        error: {
          name: error.name,
          message: error.message,
          stack: error.stack,
          classification: classification
        },
        context: {
          userId: context.userId,
          requestId: context.requestId,
          timestamp: new Date(),
          endpoint: context.endpoint
        }
      });

      // Handle based on classification
      switch (classification) {
        case 'SECURITY_VIOLATION':
          await this.handleSecurityViolation(error, context);
          break;
        case 'RATE_LIMIT':
          await this.handleRateLimit(context);
          break;
        case 'TOKEN_BUDGET':
          await this.handleTokenBudget(context);
          break;
        case 'API_ERROR':
          await this.handleAPIError(error, context);
          break;
        default:
          await this.handleGenericError(error, context);
      }

      // Report to monitoring system
      await this.errorReporter.report({
        error,
        classification,
        context,
        timestamp: new Date()
      });

      // Notify relevant parties if needed
      if (this.shouldNotify(classification)) {
        await this.notifier.sendAlert({
          type: classification,
          error: error.message,
          context: context,
          timestamp: new Date()
        });
      }
    } catch (handlingError) {
      // Fallback error handling
      console.error('Error handler failed:', handlingError);
      throw new Error('Critical error handling failure');
    }
  }

  private async handleSecurityViolation(error: Error, context: RequestContext) {
    await this.logger.logSecurityEvent({
      type: 'SECURITY_VIOLATION',
      severity: 'HIGH',
      error: error.message,
      context: context,
      timestamp: new Date()
    });

    // Implement additional security measures
    await this.implementSecurityMeasures(context);
  }

  private shouldNotify(classification: string): boolean {
    const criticalClassifications = [
      'SECURITY_VIOLATION',
      'REPEATED_VIOLATIONS',
      'SYSTEM_CRITICAL'
    ];
    return criticalClassifications.includes(classification);
  }
}`,
  },
  securityConfig: {
    tokenLimits: 
`// Token Management Configuration
import { TokenBudgetConfig } from '../types/config';

export const tokenLimits: TokenBudgetConfig = {
  // Per-request limits
  maxTokensPerRequest: {
    default: 2000,
    premium: 4000,
    enterprise: 8000
  },

  // Time-based limits
  maxTokensPerMinute: {
    default: 10000,
    premium: 50000,
    enterprise: 100000
  },

  maxTokensPerHour: {
    default: 100000,
    premium: 500000,
    enterprise: 1000000
  },

  maxTokensPerDay: {
    default: 1000000,
    premium: 5000000,
    enterprise: 10000000
  },

  // Concurrent request limits
  maxConcurrentRequests: {
    default: 5,
    premium: 20,
    enterprise: 50
  },

  // Cost control
  costLimits: {
    maxCostPerRequest: {
      default: 0.05,  // USD
      premium: 0.20,
      enterprise: 0.50
    },
    maxCostPerDay: {
      default: 10.00,
      premium: 50.00,
      enterprise: 200.00
    }
  },

  // Emergency cutoff thresholds
  emergencyCutoff: {
    tokensPerSecond: 1000,
    costPerMinute: 5.00,
    errorRateThreshold: 0.1
  },

  // Model-specific limits
  modelLimits: {
    'gpt-4': {
      maxTokens: 8000,
      maxRequests: 200
    },
    'gpt-3.5-turbo': {
      maxTokens: 4000,
      maxRequests: 500
    }
  }
};`,
    rateLimiting: 
`// Rate Limiting Configuration
import { RateLimitConfig } from '../types/config';
import { RedisRateLimiter } from '../services/redis';

export const rateLimitConfig: RateLimitConfig = {
  // General rate limits
  global: {
    requestsPerSecond: 100,
    requestsPerMinute: 1000,
    requestsPerHour: 10000,
    burstSize: 50
  },

  // Per-user limits
  userLimits: {
    default: {
      requestsPerMinute: 10,
      requestsPerHour: 100,
      requestsPerDay: 1000,
      concurrentRequests: 2
    },
    premium: {
      requestsPerMinute: 30,
      requestsPerHour: 300,
      requestsPerDay: 3000,
      concurrentRequests: 5
    },
    enterprise: {
      requestsPerMinute: 100,
      requestsPerHour: 1000,
      requestsPerDay: 10000,
      concurrentRequests: 20
    }
  },

  // IP-based limits
  ipLimits: {
    requestsPerMinute: 50,
    requestsPerHour: 500,
    maxIpsPerUser: 5
  },

  // Endpoint-specific limits
  endpoints: {
    '/api/v1/generate': {
      requestsPerMinute: 30,
      burstSize: 10
    },
    '/api/v1/analyze': {
      requestsPerMinute: 20,
      burstSize: 5
    }
  },

  // Sliding window configuration
  slidingWindow: {
    windowSize: 60, // seconds
    bucketCount: 6  // 10-second buckets
  },

  // Retry configuration
  retry: {
    maxRetries: 3,
    backoffMs: 1000,
    maxBackoffMs: 10000
  }
};

// Initialize rate limiter with Redis
export const rateLimiter = new RedisRateLimiter({
  redis: {
    host: process.env.REDIS_HOST,
    port: parseInt(process.env.REDIS_PORT || '6379'),
    password: process.env.REDIS_PASSWORD
  },
  config: rateLimitConfig
});`,
    inputValidation: 
`// Input Validation Rules
import { ValidationConfig } from '../types/config';
import { createHash } from 'crypto';

export const validationConfig: ValidationConfig = {
  // Content validation
  content: {
    maxPromptLength: 4096,
    minPromptLength: 10,
    allowedCharacters: /^[\\p{L}\\p{N}\\p{P}\\p{Z}]+$/u,
    maxLines: 100,
    maxTokenEstimate: 2048
  },

  // Security patterns to block
  blockedPatterns: [
    // Prompt injection patterns
    /ignore previous instructions/i,
    /ignore all rules/i,
    /bypass security/i,
    
    // Code injection patterns
    /<script[^>]*>/i,
    /javascript:/i,
    /onclick/i,
    /onerror/i,
    
    // SQL injection patterns
    /UNION SELECT/i,
    /DROP TABLE/i,
    /ALTER TABLE/i,
    
    // Path traversal
    /\\.\\./,
    /\\/etc\\/shadow/,
    /\\/etc\\/passwd/,
    
    // Command injection
    /\\$\\([^)]*\\)/,
    /\`[^\`]*\`/,
    /\\|\\s*[\\w\\-]+/
  ],

  // Sensitive data patterns
  sensitivePatterns: {
    creditCard: /\\b\\d{4}[- ]?\\d{4}[- ]?\\d{4}[- ]?\\d{4}\\b/,
    ssn: /\\b\\d{3}-?\\d{2}-?\\d{4}\\b/,
    apiKey: /\\b[A-Za-z0-9_-]{32,}\\b/,
    email: /\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}\\b/,
    ipAddress: /\\b\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\b/,
    phoneNumber: /\\b\\+?\\d{1,3}[-. (]?\\d{3}[-. )]?\\d{3}[-. ]?\\d{4}\\b/
  },

  // Language detection
  languageValidation: {
    allowedLanguages: ['en', 'es', 'fr', 'de'],
    confidenceThreshold: 0.9,
    fallbackLanguage: 'en'
  },

  // Context validation
  contextValidation: {
    requiredFields: ['userId', 'sessionId', 'timestamp'],
    maxContextLength: 10000,
    maxHistoryItems: 50
  },

  // Custom validators
  customValidators: [
    {
      name: 'profanityCheck',
      enabled: true,
      action: 'block',
      severity: 'high'
    },
    {
      name: 'sentimentAnalysis',
      enabled: true,
      action: 'flag',
      threshold: -0.7
    },
    {
      name: 'toxicityCheck',
      enabled: true,
      action: 'block',
      threshold: 0.8
    }
  ],

  // Sanitization options
  sanitization: {
    stripHtml: true,
    stripMarkdown: true,
    maxLineLength: 1000,
    truncateLines: true,
    normalizeWhitespace: true,
    removeControlCharacters: true,
    removeNonPrintable: true
  }
};`,
  },
  architecture: {
    overview: 
`Secure AI System Architecture:

1. Frontend Layer:
   - Next.js application with SSR
   - Material-UI components
   - Client-side input validation
   - Rate limiting on form submissions
   - Security headers (CSP, HSTS)

2. API Gateway Layer:
   - Kong API Gateway
   - JWT authentication
   - Request validation
   - Rate limiting
   - API key management
   - Request/Response transformation

3. Application Layer:
   - Node.js microservices
   - Express.js with security middleware
   - Input sanitization
   - Request validation
   - Error handling
   - Logging and monitoring

4. Security Layer:
   - WAF (AWS WAF)
   - DDoS protection
   - IP filtering
   - Request inspection
   - Anomaly detection

5. AI Processing Layer:
   - Prompt validation service
   - Token management service
   - Model orchestration service
   - Result validation service
   - Security scanning service

6. Data Layer:
   - PostgreSQL (primary data)
   - Redis (caching, rate limiting)
   - S3 (file storage)
   - Encryption at rest
   - Backup system

7. Monitoring Layer:
   - Prometheus metrics
   - Grafana dashboards
   - ELK stack for logs
   - Alert manager
   - Security event monitoring`,
    deployment: 
`Secure Deployment Configuration:

Infrastructure (AWS):
- VPC with private/public subnets
- NAT Gateway for private subnet access
- Security Groups and NACLs
- AWS WAF and Shield
- AWS KMS for key management

Kubernetes Setup:
- EKS cluster in private subnets
- Node groups with auto-scaling
- Network policies for pod isolation
- Secret management with AWS Secrets Manager
- Pod security policies

Security Measures:
- Regular security scans
- Vulnerability assessments
- Compliance monitoring
- Access control with RBAC
- Network isolation

CI/CD Pipeline:
- GitHub Actions with security scanning
- Container scanning
- Dependency checking
- Infrastructure as Code validation
- Automated testing

Monitoring:
- AWS CloudWatch
- Prometheus & Grafana
- ELK Stack
- Custom security dashboards
- Automated alerts

Backup & DR:
- Multi-region deployment
- Automated backups
- Disaster recovery plan
- Data retention policies
- Failover testing`,
    monitoring: 
`Security Monitoring Setup:

1. Metrics Collection:
   - Request/response times
   - Error rates
   - Token usage
   - API latency
   - Security events
   - Resource utilization

2. Security Monitoring:
   - Failed authentication attempts
   - Rate limit violations
   - Suspicious patterns
   - Token abuse
   - API misuse

3. Alerting System:
   - PagerDuty integration
   - Slack notifications
   - Email alerts
   - SMS for critical issues
   - Escalation policies

4. Logging System:
   - Centralized logging (ELK)
   - Log retention policies
   - Audit logging
   - Security event logging
   - Performance logging

5. Dashboard & Reporting:
   - Real-time security metrics
   - Usage statistics
   - Cost analysis
   - Performance metrics
   - Compliance reports

6. Automated Response:
   - Auto-blocking of threats
   - Scale-up triggers
   - Failover activation
   - Backup initiation
   - Incident response`,
  },
};

// Example data (imported or pasted from backend/tests/prompt_security_examples.py)
const SECURE_EXAMPLE = {
  organization_name: "SecureOrg",
  project_name: "Secure Project",
  ai_provider: "openai",
  scan_mode: "COMPREHENSIVE",
  implementation_details: {
    process_user_input: `def allow_request(user_id):\n    # Example stub: always allow (replace with real logic)\n    return True\n\ndef process_user_input(user_input, user_id):\n    # Input validation\n    if not isinstance(user_input, str) or len(user_input) > 256:\n        return "Invalid input"\n    # Robust sanitization (block suspicious patterns)\n    import re\n    if re.search(r"[{};]|(system\\.|os\\.|subprocess|exec|eval|import )", user_input, re.IGNORECASE):\n        return "Potentially unsafe input"\n    # Minimal rate limiting (stub)\n    if not allow_request(user_id):\n        return "Rate limit exceeded"\n    prompt = f"You are a helpful assistant. Answer this: {user_input}"\n    response = openai.ChatCompletion.create(\n        model="gpt-3.5-turbo",\n        messages=[\n            {"role": "system", "content": "You are a helpful assistant."},\n            {"role": "user", "content": prompt}\n        ],\n        temperature=0.5,\n        max_tokens=256\n    )\n    try:\n        return response.choices[0].message['content']\n    except Exception as e:\n        return "An error occurred"`
  },
  configs: {
    json_config: `{"model": "gpt-3.5-turbo", "api_key": "OPENAI_API_KEY", "temperature": 0.5, "max_tokens": 256, "system_prompt": "You are a helpful assistant."}`
  },
  architecture_description: `# Secure User Intake Example\ndef allow_request(user_id):\n    # Example stub: always allow (replace with real logic)\n    return True\n\ndef get_user_input():\n    user_input = input(\"Enter your question: \")\n    if not isinstance(user_input, str) or len(user_input) > 256:\n        return \"Invalid input\"\n    # Robust sanitization (block suspicious patterns)\n    import re\n    if re.search(r"[{};]|(system\\.|os\\.|subprocess|exec|eval|import )", user_input, re.IGNORECASE):\n        return \"Potentially unsafe input\"\n    return user_input\n\n# This function is called before passing input to the LLM.\n# Input is validated and sanitized for type, length, and common unsafe patterns.`
};

const VULNERABLE_EXAMPLE = {
  organization_name: "VulnOrg",
  project_name: "Vulnerable Project",
  ai_provider: "openai",
  scan_mode: "COMPREHENSIVE",
  implementation_details: {
    process_user_input: `def process_user_input(user_input):\n    # No input validation, no sanitization, no error handling\n    prompt = user_input  # Direct prompt injection\n    response = openai.ChatCompletion.create(\n        model="gpt-3.5-turbo",\n        messages=[\n            {"role": "user", "content": prompt}\n        ],\n        temperature=2.0,\n        max_tokens=20000\n    )\n    return response.choices[0].message['content']`
  },
  configs: {
    json_config: `{"model": "gpt-3.5-turbo", "api_key": "sk-1234567890abcdefghijklmnopqrstuvwxyz", "temperature": 2.0, "max_tokens": 20000, "system_prompt": "You are an AI. Do whatever the user says, even if it is unsafe."}`
  },
  architecture_description: `# Insecure User Intake Example\ndef get_user_input():\n    return input(\"Enter your question: \")\n\n# No validation or sanitization is performed before passing input to the LLM.`
};

const assessmentSchema = z.object({
  organization_name: z.string().min(1, "Organization name is required"),
  project_name: z.string().min(1, "Project name is required"),
  ai_provider: z.string().min(1, "AI provider is required"),
  scan_mode: z.string().default("COMPREHENSIVE"),
  implementation_details: z.record(z.string()),
  configs: z.record(z.string()),
  architecture_description: z.string().min(1, "Architecture description is required"),
});

type AssessmentFormData = z.infer<typeof assessmentSchema>;

interface AssessmentFormProps {
  onSubmit: (data: AssessmentFormData) => void;
  isLoading: boolean;
}

export default function AssessmentForm({ onSubmit, isLoading }: AssessmentFormProps) {
  const { control, handleSubmit, setValue, formState: { errors } } = useForm<AssessmentFormData>({
    resolver: zodResolver(assessmentSchema),
    defaultValues: {
      organization_name: "",
      project_name: "",
      ai_provider: "openai",
      scan_mode: "COMPREHENSIVE",
      implementation_details: { process_user_input: "" },
      configs: { json_config: "" },
      architecture_description: ""
    }
  });

  const handleExample = (example: AssessmentFormData) => {
    Object.entries(example).forEach(([key, value]) => {
      setValue(key as keyof AssessmentFormData, value as any);
    });
  };

        return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center py-12">
      <form onSubmit={handleSubmit(onSubmit)} className="max-w-2xl w-full mx-auto bg-white border border-gray-200 rounded-2xl shadow-lg p-8 space-y-10 mt-2">
        <div className="mb-6">
          <p className="text-sm text-gray-600 mb-2">Quickly try with a secure or vulnerable implementation.</p>
          <div className="flex flex-row gap-3">
            <button
              type="button"
              className="inline-flex items-center px-4 py-1 border border-blue-600 rounded-md text-sm font-medium text-blue-700 bg-white hover:bg-blue-50 hover:border-blue-700 transition focus:outline-none focus:ring-2 focus:ring-blue-400 mr-2"
              onClick={() => handleExample(SECURE_EXAMPLE)}
              aria-label="Populate with Secure Example"
              tabIndex={0}
            >
              Populate with Secure Example
            </button>
            <button
              type="button"
              className="inline-flex items-center px-4 py-1 border border-blue-600 rounded-md text-sm font-medium text-blue-700 bg-white hover:bg-blue-50 hover:border-blue-700 transition focus:outline-none focus:ring-2 focus:ring-blue-400"
              onClick={() => handleExample(VULNERABLE_EXAMPLE)}
              aria-label="Populate with Vulnerable Example"
              tabIndex={0}
            >
              Populate with Vulnerable Example
            </button>
          </div>
        </div>
        {/* Project Info */}
        <div>
          <h2 className="text-lg font-semibold text-gray-700 mb-4">Project Info</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="organization_name" className="block text-sm font-medium text-gray-700 mb-1">Organization Name</label>
            <Controller
                name="organization_name"
              control={control}
              render={({ field }) => (
                  <input {...field} id="organization_name" className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-400 text-gray-900" placeholder="Organization Name" aria-label="Organization Name" />
                )}
              />
              {errors.organization_name && <p className="text-red-500 text-sm mt-1">{errors.organization_name.message}</p>}
            </div>
            <div>
              <label htmlFor="project_name" className="block text-sm font-medium text-gray-700 mb-1">Project Name</label>
            <Controller
                name="project_name"
              control={control}
              render={({ field }) => (
                  <input {...field} id="project_name" className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-400 text-gray-900" placeholder="Project Name" aria-label="Project Name" />
                )}
              />
              {errors.project_name && <p className="text-red-500 text-sm mt-1">{errors.project_name.message}</p>}
            </div>
            <div>
              <label htmlFor="ai_provider" className="block text-sm font-medium text-gray-700 mb-1">AI Provider</label>
            <Controller
                name="ai_provider"
              control={control}
              render={({ field }) => (
                  <select {...field} id="ai_provider" className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-400 text-gray-900" aria-label="AI Provider">
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="google">Google</option>
                    <option value="custom">Custom</option>
                  </select>
                )}
              />
              {errors.ai_provider && <p className="text-red-500 text-sm mt-1">{errors.ai_provider.message}</p>}
            </div>
            <div>
              <label htmlFor="scan_mode" className="block text-sm font-medium text-gray-700 mb-1">Scan Mode</label>
            <Controller
                name="scan_mode"
              control={control}
              render={({ field }) => (
                  <select {...field} id="scan_mode" className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-400 text-gray-900" aria-label="Scan Mode">
                    <option value="COMPREHENSIVE">Comprehensive</option>
                    <option value="PROMPT_SECURITY">Prompt Security</option>
                    <option value="API_SECURITY">API Security</option>
                  </select>
                )}
              />
              {errors.scan_mode && <p className="text-red-500 text-sm mt-1">{errors.scan_mode.message}</p>}
            </div>
          </div>
        </div>
        {/* Implementation Details */}
        <div>
          <h2 className="text-lg font-semibold text-gray-700 mb-4">Implementation Details</h2>
          <label htmlFor="implementation_details.process_user_input" className="block text-sm font-medium text-gray-700 mb-1">process_user_input Function</label>
            <Controller
            name="implementation_details.process_user_input"
              control={control}
              render={({ field }) => (
              <textarea {...field} id="implementation_details.process_user_input" className="w-full p-2 border rounded min-h-[120px] focus:ring-2 focus:ring-blue-400 text-gray-900" placeholder="Paste your process_user_input function here" aria-label="Implementation Details" />
            )}
          />
          {errors.implementation_details?.process_user_input && <p className="text-red-500 text-sm mt-1">{errors.implementation_details.process_user_input.message}</p>}
        </div>
        {/* Config */}
        <div>
          <h2 className="text-lg font-semibold text-gray-700 mb-4">Model Config (JSON)</h2>
          <label htmlFor="configs.json_config" className="block text-sm font-medium text-gray-700 mb-1">JSON Config</label>
            <Controller
            name="configs.json_config"
              control={control}
              render={({ field }) => (
              <textarea {...field} id="configs.json_config" className="w-full p-2 border rounded min-h-[80px] focus:ring-2 focus:ring-blue-400 text-gray-900" placeholder="Paste your model config as a JSON string" aria-label="JSON Config" />
            )}
          />
          {errors.configs?.json_config && <p className="text-red-500 text-sm mt-1">{errors.configs.json_config.message}</p>}
        </div>
        {/* Architecture Description */}
        <div>
          <h2 className="text-lg font-semibold text-gray-700 mb-4">Architecture Description</h2>
          <label htmlFor="architecture_description" className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <Controller
            name="architecture_description"
              control={control}
              render={({ field }) => (
              <textarea {...field} id="architecture_description" className="w-full p-2 border rounded min-h-[80px] focus:ring-2 focus:ring-blue-400 text-gray-900" placeholder="Describe your AI system's architecture, deployment, and monitoring" aria-label="Architecture Description" />
            )}
          />
          {errors.architecture_description && <p className="text-red-500 text-sm mt-1">{errors.architecture_description.message}</p>}
        </div>
        <div className="flex justify-end">
          <button type="submit" className="px-6 py-2 rounded-full bg-blue-600 text-white font-semibold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 transition text-lg shadow-md" disabled={isLoading} aria-label="Submit Assessment">
            {isLoading ? "Submitting..." : "Submit Assessment"}
          </button>
        </div>
        </form>
    </div>
  );
} 