'use client';

import { Container, Box, Typography, Paper, Chip, Grid, LinearProgress, Alert } from '@mui/material';
import dynamic from 'next/dynamic';
import { useState, useRef } from 'react';
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

const ResultsDisplay = ({ results, onSubmitAnother }: { results: SecurityAssessmentResult, onSubmitAnother: () => void }) => {
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
    <Box sx={{ mt: 4, position: 'relative' }}>
      {/* Submit Another Report Button */}
      <button
        className="absolute top-4 right-4 px-4 py-2 border border-blue-600 rounded text-blue-700 bg-white hover:bg-blue-50 hover:border-blue-700 transition"
        aria-label="Submit another report"
        onClick={onSubmitAnother}
        style={{ zIndex: 10 }}
      >
        Submit Another Report
      </button>
      <Paper elevation={0} sx={{ p: 4, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Assessment Results
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" gutterBottom>
            {new Date(results.timestamp).toLocaleString()}
          </Typography>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body1" gutterBottom className="text-gray-700">
              <span className="font-semibold">Organization:</span> {results.organization_name}
            </Typography>
            <Typography variant="body1" gutterBottom className="text-gray-700">
              <span className="font-semibold">Project:</span> {results.project_name}
            </Typography>
            <Typography variant="body2" className="text-gray-600">
              <span className="font-semibold">Model:</span> {results.ai_model_used} &nbsp; | &nbsp;
              <span className="font-semibold">Tokens:</span> {results.token_usage?.prompt_tokens + results.token_usage?.completion_tokens}
            </Typography>
          </Box>
          
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
              Each finding is checked for similarity against a database of real-world vulnerabilities using pattern recognition and embedding-based analysis.
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
                    The assessment uses a two-step process: first, a large language model (LLM) scans your code and configuration for patterns that match known AI security issues. Then, each finding is checked for similarity against a database of real-world vulnerabilities to help reduce false positives.
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Box>
                  <Typography variant="subtitle1" fontWeight="500" color="primary.main" gutterBottom>
                    Embedding-Based Validation
                  </Typography>
                  <Typography variant="body2" paragraph>
                    Vector embeddings are used to compare detected issues with examples of real vulnerabilities. This helps confirm whether a finding is likely to be a true security risk or just a pattern match.
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

  const handleSubmitAnother = () => {
    setResults(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12">
      <div className="flex flex-col items-center w-full px-4">
        {/* Header Card - only show if no results */}
        {!results && (
          <div className="bg-white rounded-xl shadow-md p-8 max-w-3xl w-full mb-4 text-center">
            <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-blue-700 to-blue-400 bg-clip-text text-transparent">Parseon AI Security Analysis</h1>
            <p className="text-lg text-gray-700 mb-1">Detect and remediate security vulnerabilities in your AI implementations</p>
            <p className="text-sm text-gray-500 max-w-2xl mx-auto">
              Parseon combines LLM-powered analysis with embedding-based validation to identify AI-specific security issues like prompt injection, model vulnerabilities, and insecure configurations.
            </p>
          </div>
        )}
        {/* Form or Results */}
        <div className="w-full flex flex-col items-center">
          <div className="max-w-3xl w-full">
            {!results ? (
              <>
                {error && (
                  <div className="mb-4 w-full">
                    <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-2 rounded-md text-sm">{error}</div>
                  </div>
                )}
                <AssessmentForm onSubmit={(data) => { void handleFormSubmit(data); }} isLoading={loading} />
              </>
            ) : (
              <ResultsDisplay results={results} onSubmitAnother={handleSubmitAnother} />
            )}
          </div>
        </div>
      </div>
    </main>
  );
} 