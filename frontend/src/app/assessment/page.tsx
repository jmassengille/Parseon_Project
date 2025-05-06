'use client';

import { Container, Box, Typography, Paper, Chip, Grid, LinearProgress, Alert } from '@mui/material';
import dynamic from 'next/dynamic';
import { useState } from 'react';
import { SecurityAssessmentResult, AssessmentFormData } from '@/types/assessment';
import { AssessmentService } from '@/services/assessment_service';
import { mapFormDataToApiInput } from '@/lib/example-data';

// Fix the import to use dynamic loading with default export
const AssessmentForm = dynamic(() => import('@/components/AssessmentForm').then(mod => mod.default), { ssr: false });

// Local interface used only for displaying results
interface DisplayFinding {
  category: string;
  severity: string;
  title: string;
  description: string;
  recommendation: string;
  validationStatus: string;
  confidence: number;
}

const ResultsDisplay = ({ results }: { results: SecurityAssessmentResult }) => {
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
    validationStatus: finding.validation_info?.validated ? 'validated' : 'unverified',
    confidence: finding.confidence || 0
  })) || [];

  // Create a score breakdown from category scores
  const scoreBreakdown = results.category_scores || {};

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
          <Typography variant="body1" gutterBottom>{results.project_name}</Typography>
          <Typography variant="body2" color="text.secondary">Organization: {results.organization_name}</Typography>
        </Box>

        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" gutterBottom>Security Score Breakdown</Typography>
          <Grid container spacing={2}>
            {Object.entries(scoreBreakdown).map(([category, data]) => (
              <Grid item xs={12} sm={6} key={category}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" sx={{ mb: 1 }}>
                    {category.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box sx={{ flexGrow: 1 }}>
                      <LinearProgress 
                        variant="determinate" 
                        value={data.score} 
                        sx={{ 
                          height: 10, 
                          borderRadius: 5,
                          backgroundColor: 'grey.200',
                          '& .MuiLinearProgress-bar': {
                            borderRadius: 5,
                            backgroundColor: data.score > 80 ? 'success.main' : data.score > 60 ? 'warning.main' : 'error.main',
                          }
                        }} 
                      />
                    </Box>
                    <Typography variant="body2">{data.score}%</Typography>
                  </Box>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Box>

        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" gutterBottom>Priority Actions</Typography>
          <Grid container spacing={2}>
            {results.priority_actions?.map((action, index) => (
              <Grid item xs={12} key={index}>
                <Alert 
                  severity={action.startsWith('[HIGH]') ? 'error' : action.startsWith('[MEDIUM]') ? 'warning' : 'info'}
                  sx={{ '& .MuiAlert-message': { width: '100%' } }}
                >
                  {action}
                </Alert>
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
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" gutterBottom>{finding.title}</Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Chip 
                        label={finding.severity} 
                        color={getSeverityColor(finding.severity)}
                        size="small"
                      />
                      <Chip 
                        label={finding.validationStatus} 
                        color={finding.validationStatus === 'validated' ? 'success' : 'warning'}
                        variant="outlined"
                        size="small"
                      />
                      <Chip 
                        label={`${Math.round(finding.confidence * 100)}% confidence`}
                        color="default"
                        variant="outlined"
                        size="small"
                      />
                    </Box>
                  </Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Category: {finding.category}
                  </Typography>
                  <Typography variant="body1" paragraph>
                    {finding.description}
                  </Typography>
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    Recommendation:
                  </Typography>
                  <Typography variant="body2">
                    {finding.recommendation}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Box>

        <Box sx={{ mt: 4 }}>
          <Typography variant="subtitle2" color="text.secondary">
            Assessment Details
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Model: {results.ai_model_used} • 
            Tokens: {results.token_usage?.prompt_tokens + results.token_usage?.completion_tokens}
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default function AssessmentPage() {
  const [results, setResults] = useState<SecurityAssessmentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFormSubmit = async (formData: AssessmentFormData) => {
    setLoading(true);
    setError(null);
    try {
      const apiInput = mapFormDataToApiInput(formData);
      const result = await AssessmentService.performAssessment(apiInput);
      setResults(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during assessment');
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
          {!results ? (
            <>
              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}
              <AssessmentForm onSubmit={handleFormSubmit} isLoading={loading} />
            </>
          ) : (
            <ResultsDisplay results={results} />
          )}
        </Paper>
      </div>
    </main>
  );
} 