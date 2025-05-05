'use client';

import React from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
} from '@mui/material';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import CodeIcon from '@mui/icons-material/Code';

const navItems = [
  { label: 'Features', path: '/#features' },
  { label: 'About Me', path: '/#about' },
  { label: 'Built With', path: '/#built-with' },
  { label: 'GitHub', path: 'https://github.com/jmassengille', external: true },
];

export default function Navbar() {
  const pathname = usePathname();
  const isAssessmentPage = pathname?.includes('/assessment');

  return (
    <Box 
      component="header" 
      className="fixed w-full bg-white/80"
      sx={{
        backdropFilter: 'blur(8px)',
        zIndex: 50,
        borderBottom: '1px solid',
        borderColor: 'divider'
      }}
    >
      <Container maxWidth="lg">
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between',
          alignItems: 'center',
          py: { xs: 1.5, md: 2 }
        }}>
          <Link 
            href="/" 
            style={{ textDecoration: 'none' }}
            className="flex items-center gap-2 group"
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                transition: 'all 0.2s ease',
              }}
            >
              <CodeIcon 
                sx={{ 
                  color: '#1976d2',
                  fontSize: '1.75rem',
                }}
              />
              <Typography
                sx={{
                  fontWeight: 700,
                  fontSize: { xs: '1.25rem', md: '1.5rem' },
                  letterSpacing: '-0.02em',
                  background: 'linear-gradient(90deg, #1976d2 0%, #2196f3 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  transition: 'opacity 0.2s ease',
                  '.group:hover &': {
                    opacity: 0.9,
                  }
                }}
              >
                Parseon
              </Typography>
            </Box>
          </Link>
          
          <Box sx={{ 
            display: { xs: 'none', md: 'flex' }, 
            gap: { md: 3, lg: 4 },
            alignItems: 'center'
          }}>
            {navItems.map((item) => (
              <Link 
                key={item.label} 
                href={item.path} 
                className="text-gray-800 hover:text-[#1976d2] transition-colors duration-200"
                style={{ 
                  textDecoration: 'none',
                  fontWeight: 500
                }}
                target={item.external ? "_blank" : undefined}
                rel={item.external ? "noopener noreferrer" : undefined}
              >
                {item.label}
              </Link>
            ))}
            {!isAssessmentPage && (
              <Button
                variant="contained"
                component={Link}
                href="/assessment"
                className="transition-all duration-200"
                sx={{
                  bgcolor: '#1976d2',
                  textTransform: 'none',
                  px: 3,
                  py: 1,
                  borderRadius: '8px',
                  fontWeight: 500,
                  boxShadow: (theme) => `0 4px 14px ${theme.palette.primary.main}25`,
                  '&:hover': {
                    bgcolor: '#1565c0',
                    boxShadow: (theme) => `0 6px 20px ${theme.palette.primary.main}35`,
                    transform: 'translateY(-1px)'
                  }
                }}
              >
                Try the Assessment
              </Button>
            )}
          </Box>
        </Box>
      </Container>
    </Box>
  );
} 