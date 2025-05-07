'use client';

import { Container, Box, Typography, Paper, Chip, Grid, LinearProgress, Alert, Button } from '@mui/material';
import dynamic from 'next/dynamic';
import { useState, useEffect, useRef } from 'react';
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
  const [longWait, setLongWait] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (loading) {
      setLongWait(false);
      timerRef.current = setTimeout(() => setLongWait(true), 60000); // 60 seconds
    } else {
      if (timerRef.current) clearTimeout(timerRef.current);
      setLongWait(false);
    }
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [loading]);

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
    <Container maxWidth="lg" sx={{ py: 4 }} aria-busy={loading}>
      {loading && (
        <Box sx={{ width: '100%', mb: 3 }} role="status">
          <LinearProgress />
          <Typography sx={{ mt: 2, textAlign: 'center', color: 'primary.main', fontWeight: 500 }}>
            Analysis in progress. This may take up to 2 minutes. Please do not close this page.
          </Typography>
          {longWait && (
            <Typography sx={{ mt: 1, textAlign: 'center', color: 'text.secondary', fontStyle: 'italic' }}>
              Still working... Large projects may take longer. Thank you for your patience.
            </Typography>
          )}
        </Box>
      )}
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