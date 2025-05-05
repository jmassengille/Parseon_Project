'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Alert, Box, Button, Typography } from '@mui/material';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ p: 3 }}>
          <Alert 
            severity="error" 
            sx={{ mb: 2 }}
            action={
              <Button 
                color="inherit" 
                size="small"
                onClick={() => window.location.reload()}
              >
                Reload
              </Button>
            }
          >
            <Typography variant="h6" gutterBottom>
              Something went wrong
            </Typography>
            <Typography variant="body2">
              {this.state.error?.message || 'An unexpected error occurred'}
            </Typography>
          </Alert>
        </Box>
      );
    }

    return this.props.children;
  }
} 