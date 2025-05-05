'use client';

import { Container, Box, Typography, Paper, Chip, Grid, LinearProgress } from '@mui/material';
import dynamic from 'next/dynamic';
import { useState } from 'react';
import { AssessmentResult, type AssessmentFormData, Finding as AssessmentFinding } from '@/types/assessment';

// Fix the import to use dynamic loading with default export
const AssessmentForm = dynamic(() => import('@/components/AssessmentForm').then(mod => mod.default), { ssr: false });

// Local interface used only for displaying results
interface DisplayFinding {
  category: string;
  severity: string;
  title: string;
  description: string;
  recommendation: string;
  validationStatus?: string;
}

const ResultsDisplay = ({ results }: { results: AssessmentResult }) => {
  const getSeverityColor = (severity: string) => {
    if (!severity) return 'default';
    
    switch (severity.toLowerCase()) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  // Map the backend findings to the display format
  const displayFindings: DisplayFinding[] = results.vulnerabilities?.map(finding => ({
    category: finding.category,
    severity: finding.severity,
    title: finding.title,
    description: finding.description,
    recommendation: finding.recommendation,
    validationStatus: finding.validation_info?.validated ? 'validated' : 'unverified'
  })) || [];

  // Create a score breakdown compatible with the display
  const scoreBreakdown = {
    code_quality: results.category_scores?.API_SECURITY?.score || 0,
    security_config: results.category_scores?.CONFIGURATION?.score || 0,
    architecture: results.category_scores?.PROMPT_SECURITY?.score || 0,
    monitoring: results.category_scores?.ERROR_HANDLING?.score || 0,
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Paper elevation={0} sx={{ p: 4, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Assessment Results
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" gutterBottom>
            {new Date(results.timestamp).toLocaleString()}
          </Typography>
          
          {/* Value proposition section */}
          <Box sx={{ 
            backgroundColor: 'rgba(25, 118, 210, 0.06)', 
            p: 2, 
            borderRadius: 2, 
            mb: 3,
            border: '1px solid',
            borderColor: 'primary.light' 
          }}>
            <Typography variant="subtitle1" color="primary.main" fontWeight="500" gutterBottom>
              Parseon AI Security Assessment
            </Typography>
            <Typography variant="body2" paragraph>
              Parseon has analyzed your AI implementation using a sophisticated dual-layer approach that combines 
              <strong> advanced LLM analysis</strong> with <strong>embedding-based validation</strong> against 
              known AI security patterns and vulnerabilities.
            </Typography>
            <Typography variant="body2">
              Each finding has been evaluated using our proprietary validation system, ensuring that reported 
              vulnerabilities are backed by pattern recognition and similarity analysis against our extensive 
              database of AI security issues.
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Typography variant="h5">Overall Score: {results.overall_score}/100</Typography>
            <Chip 
              label={results.overall_risk_level} 
              color={getSeverityColor(results.overall_risk_level)} 
              variant="outlined" 
            />
          </Box>
          <Typography variant="body1">{results.project_name}</Typography>
        </Box>

        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" gutterBottom>Security Score Breakdown</Typography>
          <Grid container spacing={2}>
            {scoreBreakdown && Object.entries(scoreBreakdown).map(([key, value]) => (
              <Grid item xs={12} sm={6} key={key}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" sx={{ mb: 1 }}>
                    {key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box sx={{ flexGrow: 1 }}>
                      <LinearProgress 
                        variant="determinate" 
                        value={value} 
                        sx={{ 
                          height: 10, 
                          borderRadius: 5,
                          backgroundColor: 'grey.200',
                          '& .MuiLinearProgress-bar': {
                            borderRadius: 5,
                            backgroundColor: value > 80 ? 'success.main' : value > 60 ? 'warning.main' : 'error.main',
                          }
                        }} 
                      />
                    </Box>
                    <Typography variant="body2">{value}%</Typography>
                  </Box>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Box>

        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" gutterBottom>Validation Methodology</Typography>
          <Paper 
            elevation={0} 
            sx={{ 
              p: 3, 
              borderRadius: 2,
              border: '1px solid',
              borderColor: 'divider',
              bgcolor: 'background.default'
            }}
          >
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Box>
                  <Typography variant="subtitle1" fontWeight="500" color="primary.main" gutterBottom>
                    Two-Layer Analysis
                  </Typography>
                  <Typography variant="body2" paragraph>
                    Parseon combines broad pattern detection with targeted validation to ensure high precision.
                    Each finding undergoes validation against our database of known AI security vulnerabilities.
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Box>
                  <Typography variant="subtitle1" fontWeight="500" color="primary.main" gutterBottom>
                    Embedding-Based Validation
                  </Typography>
                  <Typography variant="body2" paragraph>
                    We use semantic similarity with cutting-edge embedding technology to validate findings
                    against known patterns, significantly reducing false positives.
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12}>
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 3, 
                  justifyContent: 'center',
                  mt: 1
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <span style={{ color: '#2e7d32', fontSize: '18px' }}>✓</span>
                    <Typography variant="body2">Validated Finding</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <span style={{ color: '#ed6c02', fontSize: '18px' }}>?</span>
                    <Typography variant="body2">Unverified Finding</Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Box>

        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" gutterBottom>Findings</Typography>
          <Grid container spacing={2}>
            {displayFindings.map((finding, index) => (
              <Grid item xs={12} key={index}>
                <Paper 
                  elevation={0} 
                  sx={{ 
                    p: 3, 
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'divider',
                    bgcolor: 'background.default'
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Typography variant="h6">{finding.title}</Typography>
                    <Chip 
                      label={finding.severity} 
                      color={getSeverityColor(finding.severity)} 
                      size="small" 
                    />
                    <Chip 
                      label={finding.category} 
                      variant="outlined" 
                      size="small" 
                    />
                    {finding.validationStatus && (
                      <Chip
                        icon={finding.validationStatus === 'validated' ? 
                          <span style={{ fontSize: '18px' }}>✓</span> : 
                          <span style={{ fontSize: '18px' }}>?</span>}
                        label={finding.validationStatus === 'validated' ? 'Validated' : 'Unverified'} 
                        variant="outlined"
                        size="small"
                        sx={{ 
                          bgcolor: finding.validationStatus === 'validated' ? 'rgba(46, 125, 50, 0.1)' : 'rgba(211, 47, 47, 0.1)',
                          borderColor: finding.validationStatus === 'validated' ? 'success.light' : 'warning.light',
                          color: finding.validationStatus === 'validated' ? 'success.dark' : 'warning.dark'
                        }}
                      />
                    )}
                  </Box>
                  <Typography variant="body1" paragraph>
                    {finding.description}
                  </Typography>
                  <Typography variant="body1">
                    <Box component="span" sx={{ color: 'text.secondary', fontWeight: 600 }}>
                      Recommendation:
                    </Box>{' '}
                    <Box component="span" sx={{ color: 'text.primary' }}>
                      {finding.recommendation}
                    </Box>
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Box>

        <Box>
          <Typography variant="h5" gutterBottom>Recommendations</Typography>
          <Grid container spacing={2}>
            {results.priority_actions && results.priority_actions.map((recommendation, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Paper 
                  elevation={0} 
                  sx={{ 
                    p: 2, 
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'divider',
                    bgcolor: 'background.default',
                    height: '100%',
                    display: 'flex',
                    alignItems: 'center'
                  }}
                >
                  <Typography variant="body1">{recommendation}</Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Paper>
    </Box>
  );
};

export default function AssessmentPage() {
  const [results, setResults] = useState<AssessmentResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleFormSubmit = async (data: AssessmentFormData) => {
    setLoading(true);
    try {
      // Convert form data to API format
      const apiInput = {
        organization_name: data.organizationName,
        project_name: data.projectName,
        ai_provider: data.aiProvider,
        implementation_details: {
          process_function: data.implementationDetails?.mainImplementation,
          prompt_handling: data.implementationDetails?.promptHandling,
          error_handling: data.implementationDetails?.errorHandling,
        },
        configs: {
          token_limits: data.securityConfig?.tokenLimits,
          rate_limiting: data.securityConfig?.rateLimiting,
          input_validation: data.securityConfig?.inputValidation,
        },
        architecture_description: data.architecture ? [
          data.architecture.overview,
          data.architecture.deployment,
          data.architecture.monitoring
        ].filter(Boolean).join('\n\n') : '',
        use_mock_data: (data as any).use_mock_data
      };
      
      // Mock API call or actual API call based on environment
      const mockEnabled = process.env.NEXT_PUBLIC_ENABLE_MOCK_API === 'true';
      
      let response;
      if (mockEnabled || (data as any).use_mock_data) {
        // Use mock data for testing - always use the mock API
        response = await fetch(`/api/mock/assessment`);
      } else {
        // Use the Next.js API route to communicate with backend
        response = await fetch('/api/assessment', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(apiInput),
        });
      }
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const responseData = await response.json();
      setResults(responseData);
    } catch (error) {
      console.error('Error submitting assessment:', error);
      alert('Failed to submit assessment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4">
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography variant="h3" component="h1" sx={{ 
            fontWeight: 700, 
            mb: 2,
            background: 'linear-gradient(90deg, #1976d2 0%, #2196f3 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            display: 'inline-block'
          }}>
            Parseon AI Security Analysis
          </Typography>
          <Typography variant="subtitle1" sx={{ 
            color: 'text.secondary', 
            maxWidth: '700px', 
            mx: 'auto',
            mb: 1
          }}>
            Detect and remediate security vulnerabilities in your AI implementations
          </Typography>
          <Typography variant="body2" sx={{ 
            color: 'text.secondary', 
            maxWidth: '700px', 
            mx: 'auto' 
          }}>
            Parseon combines LLM-powered analysis with embedding-based validation to identify 
            AI-specific security issues like prompt injection, model vulnerabilities, 
            and insecure configurations.
          </Typography>
        </Box>
        
        <Paper elevation={0} sx={{ 
          p: { xs: 2, sm: 4 }, 
          borderRadius: 2, 
          border: '1px solid', 
          borderColor: 'divider',
          mb: 6,
          maxWidth: '1000px',
          mx: 'auto'
        }}>
          <AssessmentForm onSubmit={handleFormSubmit} isLoading={loading} />
        </Paper>
        
        {results && <ResultsDisplay results={results} />}
      </div>
    </main>
  );
} 