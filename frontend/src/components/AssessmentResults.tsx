'use client';

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
  Alert
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
import { useRouter } from 'next/router';

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  marginBottom: theme.spacing(3),
}));

const ScoreBox = styled(Box)(({ theme }) => ({
  textAlign: 'center',
  padding: theme.spacing(2),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.default,
}));

const CategoryCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
}));

const ValidationBadge = styled(Badge)(({ theme }) => ({
  '& .MuiBadge-badge': {
    right: -4,
    top: -4,
  },
}));

interface AssessmentResultsProps {
  results: AssessmentResult;
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

export default function AssessmentResults({ results }: AssessmentResultsProps) {
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
    <StyledPaper sx={{ position: 'relative' }}>
      {/* Submit Another Report Button */}
      <button
        className="absolute top-4 right-4 px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 transition"
        aria-label="Submit another report"
        onClick={() => router.push('/')}
        style={{ zIndex: 10 }}
      >
        Submit Another Report
      </button>
      <Typography variant="h4" gutterBottom>
        AI Security Assessment Results
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Typography variant="h6">Project Details</Typography>
          <Typography>Organization: {results.organization_name}</Typography>
          <Typography>Project: {results.project_name}</Typography>
          <Typography>Assessment Date: {new Date(results.timestamp).toLocaleString()}</Typography>
          <Typography>Model: {results.ai_model_used}</Typography>
          <Typography>
            Tokens: {results.token_usage.prompt_tokens + results.token_usage.completion_tokens} 
            ({results.token_usage.prompt_tokens} prompt, {results.token_usage.completion_tokens} completion)
          </Typography>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <ScoreBox>
            <Typography variant="h3" color={getScoreColor(results.overall_score)}>
              {results.overall_score.toFixed(1)}
            </Typography>
            <Typography variant="h6">Overall Score</Typography>
            <Chip 
              label={`Risk Level: ${results.overall_risk_level || 'Unknown'}`}
              color={severityColors[(results.overall_risk_level || 'LOW') as keyof typeof severityColors] || 'default'}
              sx={{ mt: 1 }}
            />
          </ScoreBox>
        </Grid>
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>Category Scores</Typography>
        <Grid container spacing={2}>
          {results.category_scores && Object.entries(results.category_scores).map(([category, score]) => (
            <Grid item xs={12} sm={6} md={3} key={category}>
              <CategoryCard>
                <CardContent>
                  <Typography variant="h6" sx={{ textTransform: 'capitalize', mb: 1 }}>
                    {categoryLabels[category as keyof typeof categoryLabels] || category}
                  </Typography>
                  <Typography variant="h3" color={getScoreColor(score.score)}>
                    {score.score.toFixed(1)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {score.findings.length} Finding{score.findings.length !== 1 ? 's' : ''}
                  </Typography>
                </CardContent>
              </CategoryCard>
            </Grid>
          ))}
        </Grid>
      </Box>

      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>Priority Actions</Typography>
        <List>
          {results.priority_actions && results.priority_actions.map((action, index) => (
            <ListItem key={index}>
              <ListItemText primary={action} />
            </ListItem>
          ))}
        </List>
      </Box>

      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>Vulnerabilities</Typography>
        <List>
          {results.vulnerabilities && results.vulnerabilities.map((finding, index) => (
            <React.Fragment key={index}>
              <ListItem alignItems="flex-start">
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <ValidationBadge
                        badgeContent={
                          finding.validation_info?.validated ? 
                            <Tooltip title="Validated against known patterns">
                              <CheckCircleIcon fontSize="small" color="success" />
                            </Tooltip> : 
                            <Tooltip title="Not validated against known patterns">
                              <HelpOutlineIcon fontSize="small" color="action" />
                            </Tooltip>
                        }
                      >
                        <Typography variant="subtitle1">{finding.title}</Typography>
                      </ValidationBadge>
                      <Chip 
                        label={finding.severity || 'Unknown'}
                        color={severityColors[(finding.severity || 'LOW') as keyof typeof severityColors] || 'default'}
                        size="small"
                      />
                      <Chip 
                        label={categoryLabels[(finding.category || 'CONFIGURATION') as keyof typeof categoryLabels] || finding.category || 'Other'}
                        variant="outlined"
                        size="small"
                      />
                    </Box>
                  }
                  secondary={
                    <>
                      <Typography component="span" variant="body2" color="text.primary">
                        {finding.description}
                      </Typography>
                      {finding.validation_info && (
                        <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                          <VerifiedIcon fontSize="small" color={finding.validation_info.validated ? "success" : "disabled"} />
                          <Typography variant="body2" color="text.secondary">
                            {finding.validation_info.validated ? 'Validated' : 'Unverified'}
                            {finding.validation_info.similar_vulnerability && 
                              ` • Similar to: ${finding.validation_info.similar_vulnerability}`}
                          </Typography>
                        </Box>
                      )}
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        <strong>Recommendation:</strong> {finding.recommendation}
                      </Typography>
                      {finding.code_snippets && finding.code_snippets.length > 0 && (
                        <Box sx={{ mt: 1, p: 1, backgroundColor: 'grey.100', borderRadius: 1 }}>
                          <Typography variant="body2" component="pre" sx={{ overflow: 'auto', whiteSpace: 'pre-wrap' }}>
                            {finding.code_snippets[0]}
                          </Typography>
                        </Box>
                      )}
                    </>
                  }
                />
              </ListItem>
              {index < results.vulnerabilities.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      </Box>
    </StyledPaper>
  );
} 