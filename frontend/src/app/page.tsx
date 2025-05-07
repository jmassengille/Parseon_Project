'use client';

import { Container, Box, Typography, Button, Grid, Paper, Chip, Stack, IconButton, Avatar, Card, CardContent } from '@mui/material';
import Link from 'next/link';
import CodeIcon from '@mui/icons-material/Code';
import GitHubIcon from '@mui/icons-material/GitHub';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import SecurityIcon from '@mui/icons-material/Security';
import PsychologyIcon from '@mui/icons-material/Psychology';
import AssessmentIcon from '@mui/icons-material/Assessment';

export default function Home() {
  return (
    <Box component="main" className="min-h-screen bg-white">
      <Box className="min-h-screen flex flex-col bg-white">
        {/* Hero Section */}
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
            pt: { xs: 10, md: 16 }, 
            pb: { xs: 8, md: 12 },
            background: 'linear-gradient(180deg, rgba(25, 118, 210, 0.08) 0%, #FFFFFF 100%)',
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
              variant="h1" 
              component="h1" 
              gutterBottom 
              sx={{ 
                fontWeight: 800,
                fontSize: { xs: '2.75rem', md: '4rem' },
                mb: 3,
                color: '#1A1A1A',
                position: 'relative',
                background: 'linear-gradient(45deg, #3a7bd5, #00d2ff)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                display: 'inline-block',
                letterSpacing: '-0.02em',
              }}
            >
              Parseon
            </Typography>
            <Typography 
              variant="h4" 
              sx={{ 
                color: 'text.primary',
                mb: 2,
                fontWeight: 600,
                maxWidth: '800px',
                mx: 'auto',
                position: 'relative',
                fontSize: { xs: '1.5rem', md: '2rem' },
              }}
            >
              AI Security Assessment Tool
            </Typography>
            <Typography 
              variant="body1" 
              sx={{ 
                color: 'text.secondary',
                mb: 6,
                lineHeight: 1.8,
                fontSize: { xs: '1rem', md: '1.125rem' },
                maxWidth: '800px',
                mx: 'auto',
                position: 'relative'
              }}
            >
              Automatically assess security gaps, vulnerabilities, and risks in your AI implementations
              using advanced LLM analysis and embedding-based validation.
            </Typography>
            <Box sx={{ display: 'flex', gap: 3, justifyContent: 'center', position: 'relative' }}>
              <Button
                variant="contained"
                component={Link}
                href="/assessment"
                size="large"
                startIcon={<RocketLaunchIcon />}
                sx={{
                  textTransform: 'none',
                  px: 4,
                  py: 1.75,
                  borderRadius: '12px',
                  fontWeight: 600,
                  fontSize: '1.1rem',
                  boxShadow: '0 8px 20px rgba(0, 0, 0, 0.15)',
                  background: 'linear-gradient(45deg, #3a7bd5, #00d2ff)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #2e66b5, #00aedb)',
                    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)',
                    transform: 'translateY(-2px)'
                  }
                }}
              >
                Try It Out
              </Button>
            </Box>
          </Container>
        </Box>

        {/* Portfolio Project Description */}
        <Box 
          component="section" 
          sx={{ 
            py: { xs: 6, md: 10 },
            bgcolor: 'white'
          }}
        >
          <Container maxWidth="md" sx={{ px: 3 }}>
            <Card
              elevation={2}
              sx={{
                p: 0,
                borderRadius: 3,
                overflow: 'hidden',
                transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0 12px 24px rgba(0, 0, 0, 0.1)'
                }
              }}
            >
              <CardContent sx={{ p: 4 }}>
                <Typography 
                  variant="h5" 
                  component="h2" 
                  gutterBottom 
                  sx={{ 
                    color: '#1A1A1A',
                    fontWeight: 700,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1.5,
                    mb: 3
                  }}
                >
                  <CodeIcon sx={{ color: '#3a7bd5' }} /> Portfolio Project
                </Typography>
                <Typography color="text.secondary" paragraph sx={{ fontSize: '1.05rem', lineHeight: 1.7 }}>
                  Parseon is a portfolio project showcasing my expertise in AI security and full-stack development. 
                  It demonstrates a sophisticated approach to detecting security vulnerabilities in AI-integrated applications 
                  using a dual-layer analysis system.
                </Typography>
                <Typography color="text.secondary" sx={{ fontSize: '1.05rem', lineHeight: 1.7 }}>
                  This project was built to demonstrate practical implementation of emerging AI security patterns and best practices,
                  with a focus on identifying issues like prompt injection vulnerabilities, insecure API usage, and improper input validation.
                </Typography>
              </CardContent>
            </Card>
          </Container>
        </Box>

        {/* About Me Section */}
        <Box 
          component="section" 
          id="about"
          sx={{ 
            py: { xs: 6, md: 10 },
            bgcolor: 'rgba(25, 118, 210, 0.03)'
          }}
        >
          <Container maxWidth="md" sx={{ px: 3 }}>
            <Card
              elevation={2}
              sx={{
                p: 0,
                borderRadius: 3,
                background: 'linear-gradient(to right, #f8f9fa, #ffffff)',
                overflow: 'hidden'
              }}
            >
              <CardContent sx={{
                p: 4,
                display: 'flex',
                flexDirection: { xs: 'column', md: 'row' },
                gap: 4,
                alignItems: 'center'
              }}>
                <Box
                  sx={{
                    width: { xs: '100%', md: '30%' },
                    textAlign: 'center'
                  }}
                >
                  <Box
                    component="img"
                    src="/headshot.jpg"
                    alt="James Massengille"
                    sx={{
                      width: 140,
                      height: 140,
                      mx: 'auto',
                      borderRadius: '50%',
                      mb: 2,
                      boxShadow: '0 8px 16px rgba(0, 0, 0, 0.1)',
                      objectFit: 'cover',
                      display: 'block'
                    }}
                  />
                  <Typography
                    variant="h6"
                    sx={{
                      fontWeight: 700,
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
                      size="medium"
                      sx={{
                        color: '#3a7bd5',
                        transition: 'transform 0.2s ease',
                        '&:hover': {
                          transform: 'scale(1.1)',
                          background: 'rgba(58, 123, 213, 0.1)'
                        }
                      }}
                    >
                      <GitHubIcon />
                    </IconButton>
                    <IconButton 
                      href="https://www.linkedin.com/in/james-massengille-800a3315b/" 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      size="medium"
                      sx={{
                        color: '#3a7bd5',
                        transition: 'transform 0.2s ease',
                        '&:hover': {
                          transform: 'scale(1.1)',
                          background: 'rgba(58, 123, 213, 0.1)'
                        }
                      }}
                    >
                      <LinkedInIcon />
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
                      fontWeight: 700,
                      mb: 3
                    }}
                  >
                    About Me
                  </Typography>
                  <Typography color="text.secondary" paragraph sx={{ fontSize: '1.05rem', lineHeight: 1.7 }}>
                    I'm a cybersecurity professional pivoting into AI security, with a focus on identifying and addressing 
                    vulnerabilities specific to AI implementations. I'm passionate about building secure AI systems that 
                    organizations can deploy with confidence.
                  </Typography>
                  <Typography color="text.secondary" sx={{ fontSize: '1.05rem', lineHeight: 1.7 }}>
                    My experience with large language models, RAG architecture, and security frameworks gives me a unique 
                    perspective on AI security challenges. Parseon represents my approach to systematically assessing and 
                    validating AI security posture across different implementation patterns.
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Container>
        </Box>

        {/* Key Features */}
        <Box 
          component="section" 
          id="features"
          sx={{ 
            py: { xs: 6, md: 10 }, 
            bgcolor: 'white'
          }}
        >
          <Container maxWidth="lg" sx={{ px: 3 }}>
            <Typography 
              variant="h3" 
              component="h2" 
              textAlign="center" 
              gutterBottom 
              sx={{ 
                mb: 6, 
                color: '#1A1A1A', 
                fontWeight: 700,
                background: 'linear-gradient(45deg, #3a7bd5, #00d2ff)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                display: 'inline-block'
              }}
            >
              Key Features
            </Typography>
            <Grid container spacing={4}>
              <Grid item xs={12} md={4}>
                <Card 
                  elevation={2} 
                  sx={{ 
                    height: '100%',
                    borderRadius: 3,
                    transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-5px)',
                      boxShadow: '0 12px 24px rgba(0, 0, 0, 0.1)'
                    }
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <SecurityIcon sx={{ fontSize: '2.5rem', color: '#3a7bd5', mr: 2 }} />
                      <Typography variant="h6" color="#1A1A1A" fontWeight={700}>
                        Advanced LLM Analysis
                      </Typography>
                    </Box>
                    <Typography color="text.secondary" sx={{ fontSize: '1.05rem', lineHeight: 1.7 }}>
                      Utilizes large language models to detect complex AI security vulnerabilities with high precision
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card 
                  elevation={2} 
                  sx={{ 
                    height: '100%',
                    borderRadius: 3,
                    transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-5px)',
                      boxShadow: '0 12px 24px rgba(0, 0, 0, 0.1)'
                    }
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <PsychologyIcon sx={{ fontSize: '2.5rem', color: '#3a7bd5', mr: 2 }} />
                      <Typography variant="h6" color="#1A1A1A" fontWeight={700}>
                        Embedding-Based Validation
                      </Typography>
                    </Box>
                    <Typography color="text.secondary" sx={{ fontSize: '1.05rem', lineHeight: 1.7 }}>
                      Validates findings against known vulnerability patterns using semantic similarity for reduced false positives
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card 
                  elevation={2} 
                  sx={{ 
                    height: '100%',
                    borderRadius: 3,
                    transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-5px)',
                      boxShadow: '0 12px 24px rgba(0, 0, 0, 0.1)'
                    }
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <AssessmentIcon sx={{ fontSize: '2.5rem', color: '#3a7bd5', mr: 2 }} />
                      <Typography variant="h6" color="#1A1A1A" fontWeight={700}>
                        Interactive Reporting
                      </Typography>
                    </Box>
                    <Typography color="text.secondary" sx={{ fontSize: '1.05rem', lineHeight: 1.7 }}>
                      Provides comprehensive security reports with validated findings and actionable recommendations
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Container>
        </Box>

        {/* Built With Section */}
        <Box 
          component="section" 
          id="built-with"
          sx={{ 
            py: { xs: 6, md: 10 },
            bgcolor: 'rgba(25, 118, 210, 0.03)'
          }}
        >
          <Container maxWidth="lg" sx={{ px: 3 }}>
            <Typography 
              variant="h3" 
              component="h2" 
              textAlign="center" 
              gutterBottom 
              sx={{ 
                mb: 6, 
                color: '#1A1A1A',
                fontWeight: 700,
                background: 'linear-gradient(45deg, #3a7bd5, #00d2ff)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                display: 'inline-block'
              }}
            >
              Built With
            </Typography>
            <Box sx={{ 
              display: 'flex', 
              flexWrap: 'wrap', 
              justifyContent: 'center', 
              gap: 1.5,
              mb: 6
            }}>
              {[
                "Next.js", "React", "Material UI", "TypeScript", 
                "Python", "FastAPI", "OpenAI API", "Embeddings", "SQLAlchemy"
              ].map((tech) => (
                <Chip 
                  key={tech}
                  label={tech} 
                  sx={{ 
                    borderRadius: '8px',
                    py: 2.5,
                    px: 1,
                    fontWeight: 500,
                    bgcolor: 'white',
                    border: '1px solid rgba(58, 123, 213, 0.3)',
                    color: '#3a7bd5',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      bgcolor: 'rgba(58, 123, 213, 0.1)',
                      transform: 'translateY(-2px)'
                    }
                  }} 
                />
              ))}
            </Box>
          </Container>
        </Box>

        <Box sx={{ flexGrow: 1 }} />

        {/* Footer */}
        <Box 
          component="footer" 
          sx={{ 
            bgcolor: '#0A1628',
            color: 'white',
            py: 8
          }}
        >
          <Container maxWidth="lg">
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <Typography 
                variant="h5" 
                gutterBottom 
                sx={{ 
                  fontWeight: 700, 
                  background: 'linear-gradient(45deg, #3a7bd5, #00d2ff)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  display: 'inline-block',
                  mb: 2
                }}
              >
                Parseon
              </Typography>
              <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.8)', maxWidth: '600px', mx: 'auto' }}>
                A portfolio project for AI security assessment
              </Typography>
            </Box>
            
            <Box sx={{ textAlign: 'center', mb: 5 }}>
              <Stack 
                direction="row" 
                spacing={3} 
                justifyContent="center"
              >
                <IconButton 
                  href="https://github.com/jmassengille" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  sx={{ 
                    color: 'white',
                    transition: 'transform 0.2s ease, background-color 0.2s ease',
                    '&:hover': {
                      transform: 'scale(1.1)',
                      bgcolor: 'rgba(255,255,255,0.1)'
                    }
                  }}
                  aria-label="GitHub"
                >
                  <GitHubIcon />
                </IconButton>
                <IconButton 
                  href="https://www.linkedin.com/in/james-massengille-800a3315b/" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  sx={{ 
                    color: 'white',
                    transition: 'transform 0.2s ease, background-color 0.2s ease',
                    '&:hover': {
                      transform: 'scale(1.1)',
                      bgcolor: 'rgba(255,255,255,0.1)'
                    }
                  }} 
                  aria-label="LinkedIn"
                >
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
