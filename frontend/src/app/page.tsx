'use client';

import { Container, Box, Typography, Button, Grid, Paper, Chip, Stack, IconButton, Avatar } from '@mui/material';
import Link from 'next/link';
import CodeIcon from '@mui/icons-material/Code';
import GitHubIcon from '@mui/icons-material/GitHub';
import LinkedInIcon from '@mui/icons-material/LinkedIn';

export default function Home() {
  return (
    <Box component="main" className="min-h-screen bg-white">
      <Box className="min-h-screen flex flex-col bg-white">
        <Box 
          component="section" 
          sx={{ 
            width: '100vw',
            position: 'relative',
            left: '50%',
            right: '50%',
            marginLeft: '-50vw',
            marginRight: '-50vw',
            overflow: 'hidden',
            pt: 16, 
            pb: 10,
            background: 'linear-gradient(180deg, rgba(25, 118, 210, 0.05) 0%, #FFFFFF 100%)',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: `
                radial-gradient(80% 80% at 50% -20%, rgba(25, 118, 210, 0.15) 0%, rgba(255, 255, 255, 0) 100%),
                radial-gradient(50% 50% at 80% 10%, rgba(33, 150, 243, 0.1) 0%, rgba(255, 255, 255, 0) 100%),
                radial-gradient(50% 50% at 20% 10%, rgba(25, 118, 210, 0.1) 0%, rgba(255, 255, 255, 0) 100%)
              `,
              zIndex: 0
            }
          }}
        >
          <Container maxWidth="lg" sx={{ textAlign: 'center', position: 'relative', zIndex: 1, px: 3 }}>
            <Typography 
              variant="h2" 
              component="h1" 
              gutterBottom 
              sx={{ 
                fontWeight: 700,
                fontSize: { xs: '2.5rem', md: '3.5rem' },
                mb: 3,
                color: '#1A1A1A',
                position: 'relative',
                background: 'linear-gradient(90deg, #1976d2 0%, #2196f3 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                display: 'inline-block'
              }}
            >
              Parseon
            </Typography>
            <Typography 
              variant="h5" 
              sx={{ 
                color: 'text.primary',
                mb: 2,
                fontWeight: 500,
                maxWidth: '800px',
                mx: 'auto',
                position: 'relative'
              }}
            >
              AI Security Assessment Tool
            </Typography>
            <Typography 
              variant="body1" 
              sx={{ 
                color: 'text.secondary',
                mb: 4,
                lineHeight: 1.6,
                maxWidth: '800px',
                mx: 'auto',
                position: 'relative'
              }}
            >
              Automatically assess security gaps, vulnerabilities, and risks in your AI implementations
              using advanced LLM analysis and embedding-based validation.
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', position: 'relative' }}>
              <Button
                variant="contained"
                component={Link}
                href="/assessment"
                className="transition-all duration-200"
                sx={{
                  bgcolor: '#1976d2',
                  textTransform: 'none',
                  px: 4,
                  py: 1.5,
                  borderRadius: '8px',
                  fontWeight: 500,
                  boxShadow: (theme) => `0 4px 14px ${theme.palette.primary.main}25`,
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    bgcolor: '#1565c0',
                    boxShadow: (theme) => `0 6px 20px ${theme.palette.primary.main}35`,
                    transform: 'translateY(-1px)'
                  }
                }}
              >
                Try the Assessment
              </Button>
            </Box>
          </Container>
        </Box>

        {/* Portfolio Project Description */}
        <Box 
          component="section" 
          sx={{ 
            py: 8,
            bgcolor: 'white'
          }}
        >
          <Container maxWidth="md" sx={{ px: 3 }}>
            <Paper
              elevation={0}
              sx={{
                p: 4,
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'divider',
                mb: 6
              }}
            >
              <Typography 
                variant="h5" 
                component="h2" 
                gutterBottom 
                sx={{ 
                  color: '#1A1A1A',
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  mb: 2
                }}
              >
                <CodeIcon color="primary" /> Portfolio Project
              </Typography>
              <Typography color="text.secondary" paragraph>
                Parseon is a portfolio project showcasing my expertise in AI security and full-stack development. 
                It demonstrates a sophisticated approach to detecting security vulnerabilities in AI-integrated applications 
                using a dual-layer analysis system.
              </Typography>
              <Typography color="text.secondary">
                This project was built to demonstrate practical implementation of emerging AI security patterns and best practices,
                with a focus on identifying issues like prompt injection vulnerabilities, insecure API usage, and improper input validation.
              </Typography>
            </Paper>
          </Container>
        </Box>

        {/* About Me Section */}
        <Box 
          component="section" 
          id="about"
          sx={{ 
            py: 8,
            bgcolor: 'white'
          }}
        >
          <Container maxWidth="md" sx={{ px: 3 }}>
            <Paper
              elevation={0}
              sx={{
                p: 4,
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'divider',
                mb: 6,
                display: 'flex',
                flexDirection: { xs: 'column', md: 'row' },
                gap: 4,
                alignItems: 'center'
              }}
            >
              <Box
                sx={{
                  width: { xs: '100%', md: '30%' },
                  textAlign: 'center'
                }}
              >
                <Avatar
                  sx={{
                    width: 120,
                    height: 120,
                    mx: 'auto',
                    bgcolor: 'primary.main',
                    fontSize: '2.5rem',
                    mb: 2
                  }}
                >
                  JM
                </Avatar>
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 600,
                    mb: 1
                  }}
                >
                  James Massengille
                </Typography>
                <Stack
                  direction="row"
                  spacing={1}
                  justifyContent="center"
                  sx={{ mb: 2 }}
                >
                  <IconButton 
                    href="https://github.com/jmassengille" 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    size="small"
                    color="primary"
                  >
                    <GitHubIcon fontSize="small" />
                  </IconButton>
                  <IconButton 
                    href="https://www.linkedin.com/in/james-massengille-800a3315b/" 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    size="small"
                    color="primary"
                  >
                    <LinkedInIcon fontSize="small" />
                  </IconButton>
                </Stack>
              </Box>
              
              <Box sx={{ width: { xs: '100%', md: '70%' } }}>
                <Typography 
                  variant="h5" 
                  component="h2" 
                  gutterBottom 
                  sx={{ 
                    color: '#1A1A1A',
                    fontWeight: 600,
                    mb: 2
                  }}
                >
                  About Me
                </Typography>
                <Typography color="text.secondary" paragraph>
                  I'm a cybersecurity professional pivoting into AI security, with a focus on identifying and addressing 
                  vulnerabilities specific to AI implementations. I'm passionate about building secure AI systems that 
                  organizations can deploy with confidence.
                </Typography>
                <Typography color="text.secondary">
                  My experience with large language models, RAG architecture, and security frameworks gives me a unique 
                  perspective on AI security challenges. Parseon represents my approach to systematically assessing and 
                  validating AI security posture across different implementation patterns.
                </Typography>
              </Box>
            </Paper>
          </Container>
        </Box>

        <Box 
          component="section" 
          id="features"
          sx={{ 
            py: 8, 
            bgcolor: 'rgba(25, 118, 210, 0.03)'
          }}
        >
          <Container maxWidth="lg" sx={{ px: 3 }}>
            <Typography 
              variant="h4" 
              component="h2" 
              textAlign="center" 
              gutterBottom 
              sx={{ mb: 6, color: '#1A1A1A' }}
            >
              Key Features
            </Typography>
            <Grid container spacing={4}>
              <Grid item xs={12} md={4}>
                <Paper 
                  elevation={0} 
                  sx={{ 
                    p: 4,
                    height: '100%',
                    bgcolor: 'white',
                    borderRadius: '8px',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                  }}
                >
                  <Typography variant="h6" gutterBottom color="primary.dark" fontWeight={600}>
                    Advanced LLM Analysis
                  </Typography>
                  <Typography color="text.secondary">
                    Utilizes large language models to detect complex AI security vulnerabilities with high precision
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={4}>
                <Paper 
                  elevation={0} 
                  sx={{ 
                    p: 4,
                    height: '100%',
                    bgcolor: 'white',
                    borderRadius: '8px',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                  }}
                >
                  <Typography variant="h6" gutterBottom color="primary.dark" fontWeight={600}>
                    Embedding-Based Validation
                  </Typography>
                  <Typography color="text.secondary">
                    Validates findings against known vulnerability patterns using semantic similarity for reduced false positives
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={4}>
                <Paper 
                  elevation={0} 
                  sx={{ 
                    p: 4,
                    height: '100%',
                    bgcolor: 'white',
                    borderRadius: '8px',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                  }}
                >
                  <Typography variant="h6" gutterBottom color="primary.dark" fontWeight={600}>
                    Interactive Reporting
                  </Typography>
                  <Typography color="text.secondary">
                    Provides comprehensive security reports with validated findings and actionable recommendations
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          </Container>
        </Box>

        {/* Built With Section */}
        <Box 
          component="section" 
          id="built-with"
          sx={{ 
            py: 8,
            bgcolor: 'white'
          }}
        >
          <Container maxWidth="lg" sx={{ px: 3 }}>
            <Typography 
              variant="h4" 
              component="h2" 
              textAlign="center" 
              gutterBottom 
              sx={{ mb: 4, color: '#1A1A1A' }}
            >
              Built With
            </Typography>
            <Stack 
              direction="row" 
              spacing={1} 
              useFlexGap 
              flexWrap="wrap" 
              justifyContent="center"
              sx={{ mb: 6 }}
            >
              <Chip label="Next.js" color="primary" variant="outlined" />
              <Chip label="React" color="primary" variant="outlined" />
              <Chip label="Material UI" color="primary" variant="outlined" />
              <Chip label="TypeScript" color="primary" variant="outlined" />
              <Chip label="Python" color="primary" variant="outlined" />
              <Chip label="FastAPI" color="primary" variant="outlined" />
              <Chip label="OpenAI API" color="primary" variant="outlined" />
              <Chip label="Embeddings" color="primary" variant="outlined" />
              <Chip label="SQLAlchemy" color="primary" variant="outlined" />
            </Stack>
          </Container>
        </Box>

        <Box sx={{ flexGrow: 1 }} />

        <Box 
          component="footer" 
          sx={{ 
            bgcolor: '#0A1628',
            color: 'white',
            py: 6
          }}
        >
          <Container maxWidth="lg">
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <Typography 
                variant="h6" 
                gutterBottom 
                sx={{ 
                  fontWeight: 600, 
                  background: 'linear-gradient(90deg, #1976d2 0%, #2196f3 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  display: 'inline-block'
                }}
              >
                Parseon
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                A portfolio project for AI security assessment
              </Typography>
            </Box>
            
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <Stack 
                direction="row" 
                spacing={2} 
                justifyContent="center"
              >
                <IconButton href="https://github.com/jmassengille" target="_blank" rel="noopener noreferrer" color="inherit" aria-label="GitHub">
                  <GitHubIcon />
                </IconButton>
                <IconButton href="https://www.linkedin.com/in/james-massengille-800a3315b/" target="_blank" rel="noopener noreferrer" color="inherit" aria-label="LinkedIn">
                  <LinkedInIcon />
                </IconButton>
              </Stack>
            </Box>
            
            <Typography 
              variant="body2" 
              sx={{ 
                color: 'rgba(255,255,255,0.7)', 
                textAlign: 'center',
                borderTop: '1px solid rgba(255,255,255,0.1)',
                pt: 4
              }}
            >
              © {new Date().getFullYear()} · Portfolio Project · Not for commercial use
            </Typography>
          </Container>
        </Box>
      </Box>
    </Box>
  );
}
