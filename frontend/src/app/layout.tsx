'use client';

import { Inter, Plus_Jakarta_Sans } from 'next/font/google';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Navbar from '@/components/Navbar';
import "./globals.css";

const inter = Inter({ subsets: ['latin'] });
const plusJakarta = Plus_Jakarta_Sans({ 
  subsets: ['latin'],
  display: 'swap',
});

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
      dark: '#1565c0',
      light: '#2196f3'
    },
    background: {
      default: '#ffffff',
      paper: '#ffffff',
    },
    text: {
      primary: '#1A1A1A',
      secondary: '#666666'
    }
  },
  typography: {
    fontFamily: plusJakarta.style.fontFamily,
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
      lineHeight: 1.2,
      letterSpacing: '-0.02em',
      '@media (min-width:600px)': {
        fontSize: '3rem',
      },
    },
    h2: {
      fontWeight: 700,
      fontSize: '2rem',
      lineHeight: 1.3,
      letterSpacing: '-0.02em',
      '@media (min-width:600px)': {
        fontSize: '2.5rem',
      },
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.5rem',
      lineHeight: 1.4,
      letterSpacing: '-0.01em',
      '@media (min-width:600px)': {
        fontSize: '2rem',
      },
    },
    body1: {
      fontFamily: inter.style.fontFamily,
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontFamily: inter.style.fontFamily,
      fontSize: '0.875rem',
      lineHeight: 1.6,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '8px',
          transition: 'all 0.2s ease',
          fontWeight: 500,
        },
        contained: {
          boxShadow: '0 2px 4px rgba(0,102,255,0.1)',
          '&:hover': {
            boxShadow: '0 4px 8px rgba(0,102,255,0.2)',
            transform: 'translateY(-1px)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: '12px',
          transition: 'all 0.2s ease',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '12px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
          '&:hover': {
            boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
            transform: 'translateY(-2px)',
          },
          transition: 'all 0.2s ease',
        },
      },
    },
  },
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Navbar />
          <main className="min-h-screen bg-white pt-[72px] antialiased">
            {children}
          </main>
        </ThemeProvider>
      </body>
    </html>
  );
}
