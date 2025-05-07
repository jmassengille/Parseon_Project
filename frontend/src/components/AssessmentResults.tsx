'use client';
import { useRouter } from 'next/navigation'; // <-- for /pages directory
import React from "react";
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Chip,
  Grid,
  Divider,
  CircularProgress,
  Card,
  CardContent,
  Tooltip,
  Badge,
  Alert,
  LinearProgress,
  Button
} from '@mui/material';
import { styled } from '@mui/material/styles';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import VerifiedIcon from '@mui/icons-material/Verified';
import { AssessmentResult, Finding } from "../types/assessment";
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import RemoveIcon from '@mui/icons-material/Remove';
import { Document, Page, Text, View, StyleSheet } from '@react-pdf/renderer';


const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  marginBottom: theme.spacing(3),
}));

const ScoreBox = styled(Box)(({ theme }) => ({
  textAlign: 'center',
  padding: theme.spacing(2),
  borderRadius: theme.shape.borderRadius * 2,
  backgroundColor: theme.palette.background.default,
  boxShadow: theme.shadows[1],
  marginBottom: theme.spacing(2),
}));

const CategoryCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  borderRadius: theme.shape.borderRadius * 2,
  boxShadow: theme.shadows[1],
}));

const ValidationBadge = styled(Badge)(({ theme }) => ({
  '& .MuiBadge-badge': {
    right: -4,
    top: -4,
  },
}));

const ValidationMethodologyBox = styled(Box)(({ theme }) => ({
  border: `1.5px solid #90caf9`,
  background: '#e3f2fd',
  borderRadius: theme.shape.borderRadius * 2,
  padding: theme.spacing(2),
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1.5),
  marginTop: theme.spacing(1.5),
  marginBottom: theme.spacing(1.5),
  minHeight: 40,
}));

interface AssessmentResultsProps {
  results: AssessmentResult;
  onSubmitAnother?: () => void;
}

const severityColors = {
  'CRITICAL': 'error',
  'HIGH': 'error',
  'MEDIUM': 'warning',
  'LOW': 'success',
} as const;

const categoryLabels = {
  'API_SECURITY': 'API Security',
  'PROMPT_SECURITY': 'Prompt Security',
  'CONFIGURATION': 'Configuration',
  'ERROR_HANDLING': 'Error Handling',
} as const;

class AssessmentResultsErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('AssessmentResults error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Alert severity="error" sx={{ mt: 2 }}>
          <Typography variant="h6">Something went wrong</Typography>
          <Typography variant="body2">{this.state.error?.message}</Typography>
        </Alert>
      );
    }

    return this.props.children;
  }
}

// PDF Styles
const styles = StyleSheet.create({
  page: {
    padding: 30,
    backgroundColor: '#ffffff',
  },
  header: {
    marginBottom: 20,
    borderBottom: '1px solid #e0e0e0',
    paddingBottom: 10,
  },
  title: {
    fontSize: 24,
    marginBottom: 10,
    color: '#1976d2',
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
    marginBottom: 5,
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    marginBottom: 10,
    color: '#1976d2',
  },
  finding: {
    marginBottom: 15,
    padding: 10,
    backgroundColor: '#f5f5f5',
  },
  findingTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  findingText: {
    fontSize: 12,
    marginBottom: 5,
  },
  scoreSection: {
    marginBottom: 20,
  },
  scoreItem: {
    marginBottom: 10,
  },
  recommendation: {
    fontSize: 12,
    marginBottom: 5,
  },
});

// PDF Document Component
const AssessmentPDF = ({ results }: { results: AssessmentResult }) => (
  <Document>
    <Page size="A4" style={styles.page}>
      <View style={styles.header}>
        <Text style={styles.title}>AI Security Assessment Report</Text>
        <Text style={styles.subtitle}>Project: {results.project_name}</Text>
        <Text style={styles.subtitle}>Organization: {results.organization_name}</Text>
        <Text style={styles.subtitle}>Date: {new Date(results.timestamp).toLocaleDateString()}</Text>
      </View>

      <View style={styles.scoreSection}>
        <Text style={styles.sectionTitle}>Overall Score: {results.overall_score}%</Text>
        <Text style={styles.subtitle}>Risk Level: {results.overall_risk_level}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Security Score Breakdown</Text>
        <Text style={styles.findingText}>API Security: {results.category_scores.API_SECURITY.score}%</Text>
        <Text style={styles.findingText}>Prompt Security: {results.category_scores.PROMPT_SECURITY.score}%</Text>
        <Text style={styles.findingText}>Configuration: {results.category_scores.CONFIGURATION.score}%</Text>
        <Text style={styles.findingText}>Error Handling: {results.category_scores.ERROR_HANDLING.score}%</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Key Findings</Text>
        {results.vulnerabilities.map((finding, index) => (
          <View key={index} style={styles.finding}>
            <Text style={styles.findingTitle}>{finding.title}</Text>
            <Text style={styles.findingText}>Category: {finding.category}</Text>
            <Text style={styles.findingText}>Severity: {finding.severity}</Text>
            <Text style={styles.findingText}>Description: {finding.description}</Text>
            <Text style={styles.findingText}>Recommendation: {finding.recommendation}</Text>
          </View>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recommendations</Text>
        {results.priority_actions.map((recommendation, index) => (
          <Text key={index} style={styles.recommendation}>• {recommendation}</Text>
        ))}
      </View>
    </Page>
  </Document>
);

export default function AssessmentResults({ results, onSubmitAnother }: AssessmentResultsProps) {
  const router = useRouter();
  if (!results) return null;

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'success.main';
    if (score >= 70) return 'warning.main';
    return 'error.main';
  };

  const getAdjustmentIcon = (adjustment: string | undefined) => {
    if (!adjustment) return null;
    
    switch (adjustment) {
      case 'boosted':
        return <Tooltip title="Confidence boosted due to high validation score"><ArrowUpwardIcon color="success" fontSize="small" /></Tooltip>;
      case 'reduced':
        return <Tooltip title="Confidence reduced due to low validation score"><ArrowDownwardIcon color="error" fontSize="small" /></Tooltip>;
      case 'unchanged':
        return <Tooltip title="Confidence unchanged"><RemoveIcon color="action" fontSize="small" /></Tooltip>;
      default:
        return null;
    }
  };

  return (
    <Box sx={{ background: '#fafbfc', minHeight: '100vh', py: 4 }}>
      <Paper elevation={0} sx={{ maxWidth: 900, mx: 'auto', p: { xs: 2, md: 4 }, borderRadius: 4, border: '1.5px solid #e0e0e0', background: '#fff', position: 'relative' }}>
        {/* Submit Another Report Button - Desktop */}
        <Box sx={{ position: 'absolute', top: 24, right: 24, display: { xs: 'none', md: 'block' } }}>
          <Button
            variant="outlined"
            color="primary"
            onClick={onSubmitAnother}
            aria-label="Submit Another Report"
            tabIndex={0}
            onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { onSubmitAnother?.(); } }}
            sx={{ borderRadius: 2, fontWeight: 600, px: 3, textTransform: 'none', borderWidth: 2, '&:hover': { borderWidth: 2 } }}
          >
            Submit Another Report
          </Button>
        </Box>
        {/* Submit Another Report Button - Mobile */}
        <Box sx={{ display: { xs: 'block', md: 'none' }, mt: 1, mb: 2 }}>
          <Button
            variant="outlined"
            color="primary"
            onClick={onSubmitAnother}
            aria-label="Submit Another Report"
            tabIndex={0}
            onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { onSubmitAnother?.(); } }}
            fullWidth
            sx={{ borderRadius: 2, fontWeight: 600, py: 1.5, textTransform: 'none', borderWidth: 2, '&:hover': { borderWidth: 2 } }}
          >
            Submit Another Report
          </Button>
        </Box>
        <Typography variant="h4" gutterBottom>
          Assessment Results
        </Typography>
        <Typography variant="body2" sx={{ color: '#888', mb: 2 }}>
          {new Date(results.timestamp).toLocaleString()}
        </Typography>
        {/* Info Card */}
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
            Parseon has analyzed your AI implementation using a sophisticated dual-layer approach that combines <b>advanced LLM analysis</b> with <b>embedding-based validation</b> against known AI security patterns and vulnerabilities.
          </Typography>
          <Typography variant="body2" sx={{ color: '#333' }}>
            Each finding has been evaluated using our proprietary validation system, ensuring that reported vulnerabilities are backed by pattern recognition and similarity analysis against our extensive database of AI security issues.
          </Typography>
        </Box>
        <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Typography variant="h6">Project Details</Typography>
          <Typography>Organization: {results.organization_name}</Typography>
          <Typography>Project: {results.project_name}</Typography>
          <Typography variant="body2">Model: {results.ai_model_used}</Typography>
          <Typography variant="body2">
            Tokens: {results.token_usage.prompt_tokens + results.token_usage.completion_tokens} 
            ({results.token_usage.prompt_tokens} prompt, {results.token_usage.completion_tokens} completion)
          </Typography>
        </Grid>
        </Grid>
        {/* Score Section */}
        <Box sx={{ mb: 2 }} marginTop={2}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 0.5 }}>
            <Typography variant="h6">
              Overall Score: {results.overall_score.toFixed(1)}/100
            </Typography>
          </Box>
        </Box>
        
        {/* Category Scores */}
        <Typography variant="h6">Security Score Breakdown</Typography>
        <Grid container spacing={2} sx={{ mb: 2 }}>
          {results.category_scores && Object.entries(results.category_scores).map(([category, score], idx) => (
            <Grid item xs={12} sm={6} key={category}>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                  <Typography variant="subtitle1">{categoryLabels[category as keyof typeof categoryLabels] || category}</Typography>
                  <Typography variant="body1">{score.score.toFixed(1)}%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={score.score}
                  sx={{
                    height: 10,
                    borderRadius: 5,
                    backgroundColor: '#e0e0e0',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: '#388e3c',
                    },
                  }}
                />
              </Box>
            </Grid>
          ))}
        </Grid>
        {/* Validation Methodology */}
        <Typography variant="h6">Validation Methodology</Typography>
        <Paper elevation={0} sx={{ border: '2px solid #e0e0e0', borderRadius: 3, p: 3, mb: 4, background: '#fff' }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="body1" fontWeight={500} color="primary.main">Two-Layer Analysis</Typography>
              <Typography variant="body2" sx={{ fontSize: '0.85rem' }}>
                This assessment uses a two-step approach: first, broad pattern detection is applied to identify common AI security issues. Then, each finding is validated against a curated database of known vulnerabilities for higher accuracy.
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body1" fontWeight={500} color="primary.main">Embedding-Based Validation</Typography>
              <Typography variant="body2" sx={{ fontSize: '0.85rem' }}>
                Semantic similarity techniques are used to compare findings with established security patterns, helping to reduce false positives and highlight relevant risks in your AI implementation.
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 3, mt: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircleIcon sx={{ color: '#388e3c', fontSize: 20 }} />
                  <Typography variant="body2" sx={{ color: '#388e3c', fontWeight: 400 }}>Validated Finding</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <HelpOutlineIcon sx={{ color: '#FFA500', fontSize: 20 }} />
                  <Typography variant="body2" sx={{ color: '#FFA500', fontWeight: 400 }}>Unverified Finding</Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Paper>
        {/* Findings Section */}
        <Typography variant="h6" gutterBottom>Findings</Typography>
        {results.vulnerabilities && results.vulnerabilities.map((finding, index) => (
          <Paper key={index} elevation={0} sx={{ mb: 3, p: 2.5, border: '1.5px solid #e0e0e0', borderRadius: 3, background: '#fff' }}>
            {/* Title Row */}
            <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 1.5, mb: 0.5 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 500, color: '#222', mr: 1 }}>
                {finding.title}
              </Typography>
              
              <Box sx={{ flex: 1 }} />
              <Chip
                label={finding.severity || 'Unknown'}
                color={finding.severity === 'HIGH' ? 'error' : finding.severity === 'MEDIUM' ? 'warning' : 'default'}
                size="small"
                sx={{ fontWeight: 500, fontSize: 14, borderRadius: 999, px: 1, background: finding.severity === 'HIGH' ? '#ffebee' : finding.severity === 'MEDIUM' ? '#fff8e1' : '#f5f5f5', color: finding.severity === 'HIGH' ? '#b71c1c' : finding.severity === 'MEDIUM' ? '#b26a00' : '#333', border: 'none' }}
              />
              {finding.validation_info && (
                <Chip
                  icon={finding.validation_info.validated ? <CheckCircleIcon sx={{ fontSize: 18, color: '#388e3c' }} /> : <HelpOutlineIcon sx={{ fontSize: 18, color: '#ff9800' }} />}
                  label={finding.validation_info.validated ? 'Validated' : 'Unverified'}
                  size="small"
                  sx={{
                    fontWeight: 500,
                    fontSize: 14,
                    borderRadius: 999,
                    px: 1,
                    background: finding.validation_info.validated ? '#e8f5e9' : '#fff3e0',
                    color: finding.validation_info.validated ? '#388e3c' : '#ff9800',
                    border: 'none',
                    ml: 1
                  }}
                />
              )}
            </Box>
            {/* Description */}
            <Typography variant="body2">
              Description: {finding.description}
            </Typography>
            {/* Recommendation */}
            <Typography variant="body2">
              <span style={{ fontWeight: 500 }}>Recommendation:</span> {finding.recommendation}
            </Typography>
          </Paper>
        ))}
      </Paper>
    </Box>
  );
} 