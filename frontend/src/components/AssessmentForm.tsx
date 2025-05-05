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

// Form validation schema
const assessmentSchema = z.object({
  organizationName: z.string().min(2, "Organization name is required"),
  projectName: z.string().min(2, "Project name is required"),
  aiProvider: z.string().min(1, "AI provider is required"),
  implementationDetails: z.object({
    mainImplementation: z.string().min(1, "Main implementation is required"),
    promptHandling: z.string().min(1, "Prompt handling is required"),
    errorHandling: z.string().min(1, "Error handling is required"),
  }),
  securityConfig: z.object({
    tokenLimits: z.string().min(1, "Token limits are required"),
    rateLimiting: z.string().min(1, "Rate limiting is required"),
    inputValidation: z.string().min(1, "Input validation is required"),
  }),
  architecture: z.object({
    overview: z.string().min(1, "Architecture overview is required"),
    deployment: z.string().min(1, "Deployment details are required"),
    monitoring: z.string().min(1, "Monitoring setup is required"),
  }),
});

type AssessmentFormData = z.infer<typeof assessmentSchema>;

interface AssessmentFormProps {
  onSubmit: (data: AssessmentFormData) => void;
  isLoading: boolean;
}

export default function AssessmentForm({ onSubmit, isLoading }: AssessmentFormProps) {
  const [activeStep, setActiveStep] = useState(0);
  const [showExamplesDialog, setShowExamplesDialog] = useState(false);
  const [testDataTab, setTestDataTab] = useState(0);

  const {
    control,
    handleSubmit,
    formState: { errors },
    trigger,
    setValue,
  } = useForm<AssessmentFormData>({
    resolver: zodResolver(assessmentSchema),
    defaultValues: {
      organizationName: "",
      projectName: "",
      aiProvider: "openai",
      implementationDetails: {
        mainImplementation: "",
        promptHandling: "",
        errorHandling: "",
      },
      securityConfig: {
        tokenLimits: "",
        rateLimiting: "",
        inputValidation: "",
      },
      architecture: {
        overview: "",
        deployment: "",
        monitoring: "",
      },
    },
  });

  const handleNext = async () => {
    const fieldsToValidate = getFieldsForStep(activeStep);
    const isValid = await trigger(fieldsToValidate);
    if (isValid) {
      setActiveStep((prevStep) => prevStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const getFieldsForStep = (step: number): (keyof AssessmentFormData)[] => {
    switch (step) {
      case 0:
        return ["organizationName", "projectName", "aiProvider"];
      case 1:
        return ["implementationDetails"];
      case 2:
        return ["securityConfig"];
      case 3:
        return ["architecture"];
      default:
        return [];
    }
  };

  const handleFormSubmit = async (data: AssessmentFormData) => {
    try {
      onSubmit(data);
    } catch (err: any) {
      console.error('Error submitting assessment:', err);
      alert(`Error: ${err.message || 'An unknown error occurred'}`);
    }
  };

  const handleTestDataTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTestDataTab(newValue);
  };

  const copyTestData = () => {
    setValue("organizationName", exampleData.organizationName);
    setValue("projectName", exampleData.projectName);
    setValue("aiProvider", exampleData.aiProvider);
    setValue("implementationDetails", exampleData.implementationDetails);
    setValue("securityConfig", exampleData.securityConfig);
    setValue("architecture", exampleData.architecture);
    setShowExamplesDialog(false);
  };

  const handleTestResults = async () => {
    try {
      const testData = {
        organizationName: "Test Organization",
        projectName: "Test Project",
        aiProvider: "openai",
        use_mock_data: true
      } as any;
      
      onSubmit(testData);
    } catch (err: any) {
      console.error('Error loading test results:', err);
      alert(`Error: ${err.message || 'An unknown error occurred'}`);
    }
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ mt: 2 }}>
            <Box sx={{ mb: 3, p: 2, backgroundColor: 'rgba(25, 118, 210, 0.04)', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Enter your organization and project details to begin the AI security assessment.
                Parseon will analyze your implementation for vulnerabilities specific to AI systems.
              </Typography>
            </Box>
            <Controller
              name="organizationName"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Organization Name"
                  fullWidth
                  margin="normal"
                  error={!!errors.organizationName}
                  helperText={errors.organizationName?.message}
                />
              )}
            />
            <Controller
              name="projectName"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Project Name"
                  fullWidth
                  margin="normal"
                  error={!!errors.projectName}
                  helperText={errors.projectName?.message}
                />
              )}
            />
            <Controller
              name="aiProvider"
              control={control}
              render={({ field }) => (
                <FormControl fullWidth margin="normal">
                  <InputLabel>AI Provider</InputLabel>
                  <Select {...field} label="AI Provider">
                    <MenuItem value="openai">OpenAI</MenuItem>
                    <MenuItem value="anthropic">Anthropic</MenuItem>
                    <MenuItem value="google">Google</MenuItem>
                    <MenuItem value="custom">Custom</MenuItem>
                  </Select>
                </FormControl>
              )}
            />
          </Box>
        );
      case 1:
        return (
          <Box sx={{ mt: 2 }}>
            <Box sx={{ mb: 3, p: 2, backgroundColor: 'rgba(25, 118, 210, 0.04)', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Provide code snippets from your implementation to scan for AI-specific vulnerabilities such as 
                prompt injection, insecure API usage, and improper error handling.
              </Typography>
            </Box>
            <Controller
              name="implementationDetails.mainImplementation"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Main Implementation"
                  fullWidth
                  multiline
                  rows={4}
                  margin="normal"
                  error={!!errors.implementationDetails?.mainImplementation}
                  helperText={errors.implementationDetails?.mainImplementation?.message}
                />
              )}
            />
            <Controller
              name="implementationDetails.promptHandling"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Prompt Handling"
                  fullWidth
                  multiline
                  rows={4}
                  margin="normal"
                  error={!!errors.implementationDetails?.promptHandling}
                  helperText={errors.implementationDetails?.promptHandling?.message}
                />
              )}
            />
            <Controller
              name="implementationDetails.errorHandling"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Error Handling"
                  fullWidth
                  multiline
                  rows={4}
                  margin="normal"
                  error={!!errors.implementationDetails?.errorHandling}
                  helperText={errors.implementationDetails?.errorHandling?.message}
                />
              )}
            />
          </Box>
        );
      case 2:
        return (
          <Box sx={{ mt: 2 }}>
            <Box sx={{ mb: 3, p: 2, backgroundColor: 'rgba(25, 118, 210, 0.04)', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Detail your security controls for token usage, rate limiting, and input validation.
                Parseon will assess these measures against AI security best practices.
              </Typography>
            </Box>
            <Controller
              name="securityConfig.tokenLimits"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Token Limits & Usage Restrictions"
                  fullWidth
                  multiline
                  rows={4}
                  margin="normal"
                  error={!!errors.securityConfig?.tokenLimits}
                  helperText={errors.securityConfig?.tokenLimits?.message}
                />
              )}
            />
            <Controller
              name="securityConfig.rateLimiting"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Rate Limiting"
                  fullWidth
                  multiline
                  rows={4}
                  margin="normal"
                  error={!!errors.securityConfig?.rateLimiting}
                  helperText={errors.securityConfig?.rateLimiting?.message}
                />
              )}
            />
            <Controller
              name="securityConfig.inputValidation"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Input Validation"
                  fullWidth
                  multiline
                  rows={4}
                  margin="normal"
                  error={!!errors.securityConfig?.inputValidation}
                  helperText={errors.securityConfig?.inputValidation?.message}
                />
              )}
            />
          </Box>
        );
      case 3:
        return (
          <Box sx={{ mt: 2 }}>
            <Box sx={{ mb: 3, p: 2, backgroundColor: 'rgba(25, 118, 210, 0.04)', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Describe your AI system's architecture, deployment environment, and monitoring setup.
                Parseon will evaluate architectural security concerns specific to AI systems.
              </Typography>
            </Box>
            <Controller
              name="architecture.overview"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Architecture Overview"
                  fullWidth
                  multiline
                  rows={4}
                  margin="normal"
                  error={!!errors.architecture?.overview}
                  helperText={errors.architecture?.overview?.message}
                />
              )}
            />
            <Controller
              name="architecture.deployment"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Deployment Environment"
                  fullWidth
                  multiline
                  rows={4}
                  margin="normal"
                  error={!!errors.architecture?.deployment}
                  helperText={errors.architecture?.deployment?.message}
                />
              )}
            />
            <Controller
              name="architecture.monitoring"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Monitoring & Logging"
                  fullWidth
                  multiline
                  rows={4}
                  margin="normal"
                  error={!!errors.architecture?.monitoring}
                  helperText={errors.architecture?.monitoring?.message}
                />
              )}
            />
          </Box>
        );
      default:
        return null;
    }
  };

  return (
    <>
      <Box>
        <Box sx={{ display: "flex", justifyContent: "flex-end", gap: 2, mb: 4 }}>
          <Button
            variant="outlined"
            startIcon={<ContentCopyIcon />}
            onClick={() => setShowExamplesDialog(true)}
            sx={{
              color: "text.secondary",
              borderColor: "divider",
              "&:hover": {
                borderColor: "primary.main",
                backgroundColor: "action.hover"
              }
            }}
          >
            Load Test Data
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<VisibilityIcon />}
            onClick={handleTestResults}
            sx={{
              color: "primary.main",
              borderColor: "primary.main",
              backgroundColor: "rgba(25, 118, 210, 0.08)",
              fontWeight: 500,
              "&:hover": {
                backgroundColor: "rgba(25, 118, 210, 0.12)",
                borderColor: "primary.dark"
              }
            }}
          >
            Test Results Page
          </Button>
        </Box>

        <form onSubmit={handleSubmit(handleFormSubmit)}>
          <Stepper 
            activeStep={activeStep} 
            sx={{ 
              mb: 4,
              "& .MuiStepLabel-label": {
                color: "text.primary"
              },
              "& .MuiStepIcon-root": {
                color: "primary.main"
              },
              "& .MuiStepIcon-root.Mui-active": {
                color: "primary.main"
              },
              "& .MuiStepIcon-root.Mui-completed": {
                color: "primary.main"
              }
            }}
          >
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {renderStepContent(activeStep)}

          <Box sx={{ display: "flex", justifyContent: "space-between", mt: 4 }}>
            <Button
              disabled={activeStep === 0}
              onClick={handleBack}
              variant="outlined"
              sx={{
                color: "primary.main",
                borderColor: "primary.main",
                "&:hover": {
                  borderColor: "primary.dark",
                  backgroundColor: "action.hover"
                },
                "&.Mui-disabled": {
                  color: "action.disabled",
                  borderColor: "action.disabled"
                }
              }}
            >
              Back
            </Button>
            {activeStep === steps.length - 1 ? (
              <Button
                type="submit"
                variant="contained"
                disabled={isLoading}
                startIcon={isLoading && <CircularProgress size={20} />}
                sx={{
                  backgroundColor: "primary.main",
                  color: "primary.contrastText",
                  fontWeight: 500,
                  px: 3,
                  py: 1,
                  fontSize: "1rem",
                  "&:hover": {
                    backgroundColor: "primary.dark"
                  },
                  boxShadow: 2
                }}
              >
                {isLoading ? "Analyzing..." : "Start Assessment"}
              </Button>
            ) : (
              <Button 
                onClick={handleNext} 
                variant="contained"
                sx={{
                  backgroundColor: "primary.main",
                  color: "primary.contrastText",
                  "&:hover": {
                    backgroundColor: "primary.dark"
                  }
                }}
              >
                Next
              </Button>
            )}
          </Box>
        </form>
      </Box>

      <StyledDialog
        open={showExamplesDialog}
        onClose={() => setShowExamplesDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle sx={{ color: "text.primary" }}>Test Data</DialogTitle>
        <DialogContent>
          <Tabs 
            value={testDataTab} 
            onChange={handleTestDataTabChange}
            sx={{
              "& .MuiTab-root": {
                color: "text.secondary",
                "&.Mui-selected": {
                  color: "primary.main"
                }
              },
              "& .MuiTabs-indicator": {
                backgroundColor: "primary.main"
              }
            }}
          >
            <Tab label="Basic Info" />
            <Tab label="Implementation" />
            <Tab label="Security" />
            <Tab label="Architecture" />
          </Tabs>

          <StyledTabPanel>
            {testDataTab === 0 && (
              <Box>
                <Typography variant="h6" gutterBottom sx={{ color: "text.primary" }}>
                  Basic Information
                </Typography>
                <SyntaxHighlighter language="json" style={vscDarkPlus}>
                  {JSON.stringify({
                    organizationName: exampleData.organizationName,
                    projectName: exampleData.projectName,
                    aiProvider: exampleData.aiProvider,
                  }, null, 2)}
                </SyntaxHighlighter>
              </Box>
            )}
            {testDataTab === 1 && (
              <Box>
                <Typography variant="h6" gutterBottom sx={{ color: "text.primary" }}>
                  Implementation Details
                </Typography>
                <SyntaxHighlighter language="javascript" style={vscDarkPlus}>
                  {JSON.stringify(exampleData.implementationDetails, null, 2)}
                </SyntaxHighlighter>
              </Box>
            )}
            {testDataTab === 2 && (
              <Box>
                <Typography variant="h6" gutterBottom sx={{ color: "text.primary" }}>
                  Security Configuration
                </Typography>
                <SyntaxHighlighter language="javascript" style={vscDarkPlus}>
                  {JSON.stringify(exampleData.securityConfig, null, 2)}
                </SyntaxHighlighter>
              </Box>
            )}
            {testDataTab === 3 && (
              <Box>
                <Typography variant="h6" gutterBottom sx={{ color: "text.primary" }}>
                  Architecture Details
                </Typography>
                <SyntaxHighlighter language="javascript" style={vscDarkPlus}>
                  {JSON.stringify(exampleData.architecture, null, 2)}
                </SyntaxHighlighter>
              </Box>
            )}
          </StyledTabPanel>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setShowExamplesDialog(false)}
            sx={{
              color: "text.secondary",
              "&:hover": {
                backgroundColor: "action.hover"
              }
            }}
          >
            Cancel
          </Button>
          <Button 
            onClick={copyTestData} 
            variant="contained"
            sx={{
              backgroundColor: "primary.main",
              color: "primary.contrastText",
              "&:hover": {
                backgroundColor: "primary.dark"
              }
            }}
          >
            Copy to Form
          </Button>
        </DialogActions>
      </StyledDialog>
    </>
  );
} 