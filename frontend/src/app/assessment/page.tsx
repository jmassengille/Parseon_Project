'use client';

import { Container, Box, Typography, Paper, Chip, Grid, LinearProgress, Alert, Button } from '@mui/material';
import dynamic from 'next/dynamic';
import { useState } from 'react';
import { AssessmentResult, AssessmentFormData } from '@/types/assessment';
import { AssessmentService } from '@/services/assessment_service';
import AddIcon from '@mui/icons-material/Add';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HelpIcon from '@mui/icons-material/Help';
import AssessmentResults from '@/components/AssessmentResults';

const AssessmentForm = dynamic(() => import('@/components/AssessmentForm'), {
  ssr: false
});

export default function AssessmentPage() {
  const [results, setResults] = useState<AssessmentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFormSubmit = async (formData: AssessmentFormData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await AssessmentService.performAssessment(formData);
      setResults(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during assessment');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnother = () => {
    setResults(null);
    setError(null);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {!results ? (
        <AssessmentForm onSubmit={handleFormSubmit} loading={loading} />
      ) : (
        <AssessmentResults results={results} onSubmitAnother={handleSubmitAnother} />
      )}
    </Container>
  );
} 