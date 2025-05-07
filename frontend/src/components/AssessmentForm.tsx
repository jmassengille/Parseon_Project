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
import { AssessmentFormData, ScanMode } from '@/types/assessment';
import { secureExampleFormData, vulnerableExampleFormData } from '@/lib/example-data';
import RocketLaunchIcon from "@mui/icons-material/RocketLaunch";
import CloseIcon from "@mui/icons-material/Close";

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

const CodePreviewButton = styled(IconButton)(({ theme }: { theme: Theme }) => ({
  position: 'absolute',
  right: theme.spacing(1),
  top: theme.spacing(1),
  zIndex: 1,
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.common.white,
  '&:hover': {
    backgroundColor: theme.palette.primary.dark,
  },
  width: 36,
  height: 36,
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

// Form schema matching the API's expected input structure
const assessmentSchema = z.object({
  organization_name: z.string().min(1, "Organization name is required"),
  project_name: z.string().min(1, "Project name is required"),
  ai_provider: z.string().min(1, "AI provider is required"),
  scan_mode: z.nativeEnum(ScanMode),
  configs: z.object({
    env_file: z.string().optional(),
    json_config: z.string().optional(),
    code_snippet: z.string().optional()
  }).optional(),
  implementation_details: z.object({
    prompt_handling: z.string().optional(),
    error_handling: z.string().optional(),
    process_function: z.string().optional()
  }).optional(),
  architecture_description: z.string().optional()
}) satisfies z.ZodType<AssessmentFormData>;

type FormData = AssessmentFormData;

interface AssessmentFormProps {
  onSubmit: (data: AssessmentFormData) => void;
  loading?: boolean;
}

export default function AssessmentForm({ onSubmit, loading = false }: AssessmentFormProps) {
  const [error, setError] = useState<string | null>(null);
  const [codeDialog, setCodeDialog] = useState<{
    open: boolean;
    title: string;
    code: string;
    language: string;
  }>({
    open: false,
    title: "",
    code: "",
    language: "javascript",
  });
  
  const { control, handleSubmit, formState: { errors }, reset, watch } = useForm<FormData>({
    resolver: zodResolver(assessmentSchema),
    defaultValues: {
      scan_mode: ScanMode.COMPREHENSIVE,
      configs: {
        env_file: "",
        json_config: "",
        code_snippet: ""
      },
      implementation_details: {
        prompt_handling: "",
        error_handling: "",
        process_function: ""
      },
      architecture_description: ""
    }
  });

  const onFormSubmit = async (data: FormData) => {
    try {
      setError(null);
      onSubmit(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const loadExample = () => {
    reset(vulnerableExampleFormData);
  };
  
  const openCodeDialog = (title: string, code: string, language: string = "javascript") => {
    setCodeDialog({
      open: true,
      title,
      code,
      language,
    });
  };
  
  const closeCodeDialog = () => {
    setCodeDialog({ ...codeDialog, open: false });
  };
  
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };
  
  // Watch form fields for code preview buttons
  const watchedPromptHandling = watch("implementation_details.prompt_handling");
  const watchedErrorHandling = watch("implementation_details.error_handling");
  const watchedProcessFunction = watch("implementation_details.process_function");
  const watchedJsonConfig = watch("configs.json_config");
  const watchedArchitecture = watch("architecture_description");
  
  // Function to truncate and format code for preview
  const getCodePreview = (code: string) => {
    if (!code) return "";
    const lines = code.split("\n");
    return lines.length > 4 
      ? lines.slice(0, 4).join("\n") + "\n..."
      : code;
  };

  return (
    <>
      <Card sx={{ maxWidth: '1000px', margin: '0 auto', mb: 4, boxShadow: 3, borderRadius: 3, p: { xs: 2, md: 4 }, background: 'linear-gradient(to right, #f8f9fa, #ffffff)' }}>
        <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 2 }}>
          <Typography variant="h3" sx={{ fontWeight: 700, background: 'linear-gradient(45deg, #3a7bd5, #00d2ff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Parseon AI Security Analysis
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ fontWeight: 500 }}>
            Detect and remediate security vulnerabilities in your AI implementations
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 700}}>
            Parseon combines LLM-powered analysis with embedding-based validation to identify AI-specific security issues like prompt injection, model vulnerabilities, and insecure configurations.
          </Typography>
        </CardContent>
      </Card>
      
      <StyledPaper>
        <Paper 
          elevation={2} 
          sx={{ 
            p: 4, 
            maxWidth: 900, 
            mx: 'auto',
            borderRadius: 3, 
            background: 'linear-gradient(to bottom, #ffffff, #f8f9fa)',
            border: '1px solid #e0e0e0'
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 4 }}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={loadExample}
              startIcon={<RocketLaunchIcon />}
              sx={{ 
                borderRadius: 2, 
                fontWeight: 600, 
                px: 4, 
                py: 1.5, 
                textTransform: 'none', 
                boxShadow: 3,
                background: 'linear-gradient(45deg, #3a7bd5, #00d2ff)',
                '&:hover': {
                  background: 'linear-gradient(45deg, #2e66b5, #00aedb)',
                  boxShadow: 4
                }
              }}
            >
              Try It Out with Example
            </Button>
          </Box>
          
          <form onSubmit={handleSubmit(onFormSubmit)}>
            <Grid container spacing={3}>
              {/* Project Info */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom sx={{ mt: 2, mb: 3, color: 'text.primary', fontWeight: 600, borderBottom: '2px solid #f0f0f0', pb: 1 }}>
                  Project Info
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="organization_name"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      variant="outlined"
                      label="Organization Name"
                      fullWidth
                      error={!!errors.organization_name}
                      helperText={errors.organization_name?.message}
                      InputLabelProps={{
                        shrink: true,
                      }}
                      sx={{ 
                        '& .MuiOutlinedInput-root': {
                          borderRadius: 2,
                        }
                      }}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="project_name"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      variant="outlined"
                      label="Project Name"
                      fullWidth
                      error={!!errors.project_name}
                      helperText={errors.project_name?.message}
                      InputLabelProps={{
                        shrink: true,
                      }}
                      sx={{ 
                        '& .MuiOutlinedInput-root': {
                          borderRadius: 2,
                        }
                      }}
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Controller
                  name="ai_provider"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      variant="outlined"
                      label="AI Provider"
                      fullWidth
                      error={!!errors.ai_provider}
                      helperText={errors.ai_provider?.message}
                      InputLabelProps={{
                        shrink: true,
                      }}
                      sx={{ 
                        '& .MuiOutlinedInput-root': {
                          borderRadius: 2,
                        }
                      }}
                    />
                  )}
                />
              </Grid>

              {/* Implementation Details */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom sx={{ mt: 4, mb: 3, color: 'text.primary', fontWeight: 600, borderBottom: '2px solid #f0f0f0', pb: 1 }}>
                  Implementation Details
                </Typography>
              </Grid>
              
              <Grid item xs={12}>
                <Box sx={{ position: 'relative' }}>
                  <Controller
                    name="implementation_details.prompt_handling"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        variant="outlined"
                        label="Prompt Handling"
                        multiline
                        rows={4}
                        fullWidth
                        error={!!errors.implementation_details?.prompt_handling}
                        helperText={errors.implementation_details?.prompt_handling?.message}
                        InputLabelProps={{
                          shrink: true,
                        }}
                        sx={{ 
                          '& .MuiOutlinedInput-root': {
                            borderRadius: 2,
                            fontFamily: 'monospace'
                          }
                        }}
                      />
                    )}
                  />
                  {watchedPromptHandling && (
                    <CodePreviewButton 
                      onClick={() => openCodeDialog("Prompt Handling", watchedPromptHandling)}
                      size="small"
                      aria-label="View code"
                    >
                      <CodeIcon fontSize="small" />
                    </CodePreviewButton>
                  )}
                </Box>
              </Grid>
              
              <Grid item xs={12}>
                <Box sx={{ position: 'relative' }}>
                  <Controller
                    name="implementation_details.error_handling"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        variant="outlined"
                        label="Error Handling"
                        multiline
                        rows={4}
                        fullWidth
                        error={!!errors.implementation_details?.error_handling}
                        helperText={errors.implementation_details?.error_handling?.message}
                        InputLabelProps={{
                          shrink: true,
                        }}
                        sx={{ 
                          '& .MuiOutlinedInput-root': {
                            borderRadius: 2,
                            fontFamily: 'monospace'
                          }
                        }}
                      />
                    )}
                  />
                  {watchedErrorHandling && (
                    <CodePreviewButton 
                      onClick={() => openCodeDialog("Error Handling", watchedErrorHandling)}
                      size="small"
                      aria-label="View code"
                    >
                      <CodeIcon fontSize="small" />
                    </CodePreviewButton>
                  )}
                </Box>
              </Grid>
              
              <Grid item xs={12}>
                <Box sx={{ position: 'relative' }}>
                  <Controller
                    name="implementation_details.process_function"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        variant="outlined"
                        label="Process Function"
                        multiline
                        rows={4}
                        fullWidth
                        error={!!errors.implementation_details?.process_function}
                        helperText={errors.implementation_details?.process_function?.message}
                        InputLabelProps={{
                          shrink: true,
                        }}
                        sx={{ 
                          '& .MuiOutlinedInput-root': {
                            borderRadius: 2,
                            fontFamily: 'monospace'
                          }
                        }}
                      />
                    )}
                  />
                  {watchedProcessFunction && (
                    <CodePreviewButton 
                      onClick={() => openCodeDialog("Process Function", watchedProcessFunction, "python")}
                      size="small"
                      aria-label="View code"
                    >
                      <CodeIcon fontSize="small" />
                    </CodePreviewButton>
                  )}
                </Box>
              </Grid>

              {/* Configuration */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom sx={{ mt: 4, mb: 3, color: 'text.primary', fontWeight: 600, borderBottom: '2px solid #f0f0f0', pb: 1 }}>
                  Configuration
                </Typography>
              </Grid>
              
              <Grid item xs={12}>
                <Box sx={{ position: 'relative' }}>
                  <Controller
                    name="configs.json_config"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        variant="outlined"
                        label="JSON Configuration"
                        multiline
                        rows={4}
                        fullWidth
                        error={!!errors.configs?.json_config}
                        helperText={errors.configs?.json_config?.message}
                        InputLabelProps={{
                          shrink: true,
                        }}
                        sx={{ 
                          '& .MuiOutlinedInput-root': {
                            borderRadius: 2,
                            fontFamily: 'monospace'
                          }
                        }}
                      />
                    )}
                  />
                  {watchedJsonConfig && (
                    <CodePreviewButton 
                      onClick={() => openCodeDialog("JSON Configuration", watchedJsonConfig, "json")}
                      size="small"
                      aria-label="View code"
                    >
                      <CodeIcon fontSize="small" />
                    </CodePreviewButton>
                  )}
                </Box>
              </Grid>

              {/* Architecture */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom sx={{ mt: 4, mb: 3, color: 'text.primary', fontWeight: 600, borderBottom: '2px solid #f0f0f0', pb: 1 }}>
                  Architecture
                </Typography>
              </Grid>
              
              <Grid item xs={12}>
                <Box sx={{ position: 'relative' }}>
                  <Controller
                    name="architecture_description"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        variant="outlined"
                        label="Architecture Description"
                        multiline
                        rows={4}
                        fullWidth
                        error={!!errors.architecture_description}
                        helperText={errors.architecture_description?.message}
                        InputLabelProps={{
                          shrink: true,
                        }}
                        sx={{ 
                          '& .MuiOutlinedInput-root': {
                            borderRadius: 2,
                            fontFamily: 'monospace'
                          }
                        }}
                      />
                    )}
                  />
                  {watchedArchitecture && (
                    <CodePreviewButton 
                      onClick={() => openCodeDialog("Architecture Description", watchedArchitecture, "markdown")}
                      size="small"
                      aria-label="View code"
                    >
                      <CodeIcon fontSize="small" />
                    </CodePreviewButton>
                  )}
                </Box>
              </Grid>

              {error && (
                <Grid item xs={12}>
                  <Alert severity="error">{error}</Alert>
                </Grid>
              )}

              <Grid item xs={12}>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  fullWidth
                  disabled={loading}
                  size="large"
                  sx={{ 
                    mt: 3,
                    py: 1.5,
                    borderRadius: 2,
                    fontWeight: 600,
                    textTransform: 'none',
                    boxShadow: 3,
                    background: loading ? undefined : 'linear-gradient(45deg, #3a7bd5, #00d2ff)',
                    '&:hover': {
                      background: loading ? undefined : 'linear-gradient(45deg, #2e66b5, #00aedb)',
                      boxShadow: 4
                    }
                  }}
                >
                  {loading ? 'Analyzing...' : 'Analyze Security'}
                </Button>
              </Grid>
            </Grid>
          </form>
        </Paper>
      </StyledPaper>

      {/* Code Dialog */}
      <Dialog
        open={codeDialog.open}
        onClose={closeCodeDialog}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            boxShadow: 10
          }
        }}
      >
        <DialogTitle sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          borderBottom: '1px solid #e0e0e0',
          backgroundColor: '#f8f9fa'
        }}>
          <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
            {codeDialog.title}
          </Typography>
          <Box>
            <IconButton 
              onClick={() => copyToClipboard(codeDialog.code)}
              size="small"
              sx={{ mr: 1 }}
            >
              <ContentCopyIcon fontSize="small" />
            </IconButton>
            <IconButton 
              onClick={closeCodeDialog}
              size="small"
            >
              <CloseIcon fontSize="small" />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers sx={{ padding: 0, backgroundColor: '#282c34' }}>
          <SyntaxHighlighter
            language={codeDialog.language}
            style={vscDarkPlus}
            showLineNumbers
            customStyle={{
              margin: 0,
              borderRadius: 0,
              maxHeight: '60vh'
            }}
          >
            {codeDialog.code}
          </SyntaxHighlighter>
        </DialogContent>
      </Dialog>
    </>
  );
} 