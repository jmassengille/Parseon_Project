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
  const { control, handleSubmit, formState: { errors }, reset } = useForm<FormData>({
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

  const loadExample = (example: AssessmentFormData) => {
    reset(example);
  };

  return (
    <>
      <Card sx={{ maxWidth: '1000px', margin: '0 auto', mb: 4, boxShadow: 5, borderRadius: 3, p: { xs: 2, md: 4 }, background: '#fff' }}>
        <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 2 }}>
          <Typography variant="h3" color="primary" >
            Parseon AI Security Analysis
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Detect and remediate security vulnerabilities in your AI implementations
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 700}}>
            Parseon combines LLM-powered analysis with embedding-based validation to identify AI-specific security issues like prompt injection, model vulnerabilities, and insecure configurations.
          </Typography>
        </CardContent>
      </Card>
      <StyledPaper>
        <Paper elevation={3} sx={{ p: 4, maxWidth: 800, mx: 'auto' }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontStyle: 'italic', textAlign: 'center' }}>
            Want to test it out? Use the buttons below to load secure or vulnerable example implementations.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mb: 3 }}>
            <Button
              variant="outlined"
              color="primary"
              size="small"
              onClick={() => loadExample(secureExampleFormData)}
              sx={{ borderRadius: 2, fontWeight: 500, px: 2, textTransform: 'none', borderWidth: 2, '&:hover': { borderWidth: 2 } }}
            >
              Load Secure Example
            </Button>
            <Button
              variant="outlined"
              color="error"
              size="small"
              onClick={() => loadExample(vulnerableExampleFormData)}
              sx={{ borderRadius: 2, fontWeight: 500, px: 2, textTransform: 'none', borderWidth: 2, '&:hover': { borderWidth: 2 } }}
            >
              Load Vulnerable Example
            </Button>
          </Box>
          <form onSubmit={handleSubmit(onFormSubmit)}>
            <Grid container spacing={3}>
              {/* Project Info */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom sx={{ mt: 2, mb: 3, color: 'text.primary', fontWeight: 500 }}>
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
                    />
                  )}
                />
              </Grid>

              {/* Implementation Details */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom sx={{ mt: 4, mb: 3, color: 'text.primary', fontWeight: 500 }}>
                  Implementation Details
                </Typography>
              </Grid>
              
              <Grid item xs={12}>
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
                    />
                  )}
                />
              </Grid>
              
              <Grid item xs={12}>
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
                    />
                  )}
                />
              </Grid>

              {/* Configuration */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom sx={{ mt: 4, mb: 3, color: 'text.primary', fontWeight: 500 }}>
                  Configuration
                </Typography>
              </Grid>
              
              <Grid item xs={12}>
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
                    />
                  )}
                />
              </Grid>

              {/* Architecture */}
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom sx={{ mt: 4, mb: 3, color: 'text.primary', fontWeight: 500 }}>
                  Architecture
                </Typography>
              </Grid>
              
              <Grid item xs={12}>
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
                    />
                  )}
                />
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
                  sx={{ mt: 2 }}
                >
                  {loading ? 'Analyzing...' : 'Analyze Security'}
                </Button>
              </Grid>
            </Grid>
          </form>
          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', mt: 4 }}>
              <CircularProgress size={32} color="primary" aria-label="Loading" />
              <Typography sx={{ ml: 2, color: 'text.secondary' }}>Processing your assessment…</Typography>
            </Box>
          )}
        </Paper>
      </StyledPaper>
    </>
  );
} 