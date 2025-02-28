import React, { useState } from 'react';
import {
  Container,
  CssBaseline,
  ThemeProvider,
  Typography,
  Box,
  createTheme,
  Grow
} from '@mui/material';
import ReadmeForm from './components/ReadmeForm';
import MarkdownDisplay from './components/MarkdownDisplay';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#212121' },
    secondary: { main: '#009688' },
    background: { default: '#121212', paper: '#1E1E1E' }
  },
  typography: {
    fontFamily: 'Inter, system-ui, Avenir, Helvetica, Arial, sans-serif',
    h1: { fontWeight: 700, fontSize: '3.2rem', letterSpacing: '-0.015em' }
  }
});

const App: React.FC = () => {
  const BACKEND_SERVER = import.meta.env.BACKEND_URL || 'readme.mrigank.me';
  const [markdownResult, setMarkdownResult] = useState<string>('');

  const handleGenerate = async (profile: string, repo: string) => {
    try {
      const formData = new FormData();
      formData.append('profile', profile);
      formData.append('repo', repo);

      const response = await fetch(`https://${BACKEND_SERVER}/generate-readme`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error(`Server error: ${response.statusText}`);

      const data = await response.json();
      setMarkdownResult(data.readme);
    } catch (error: any) {
      console.error('Error generating README:', error);
      alert(`Error: ${error.message}`);
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      {/* Fixed Background */}
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundImage: `url('https://img.freepik.com/premium-vector/abstract-dark-background-zeros-ad-ones-shades-gray-colors_444390-3371.jpg?semt=ais_hybrid')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          zIndex: -1,
        }}
      />
      
      {/* Flex container for layout */}
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Navbar />

        {/* Main Content */}
        <Container maxWidth="lg" sx={{ flex: 1, pt: 8, pb: 4 }}>
          <Grow in timeout={800}>
            <Box>
              <Typography
                variant="h1"
                gutterBottom
                sx={{
                  textAlign: 'center',
                  color: '#e0e0e0',
                  textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
                  mb: 4
                }}
              >
                README Generator
              </Typography>
              <ReadmeForm onGenerate={handleGenerate} />
              {markdownResult && <MarkdownDisplay markdown={markdownResult} />}
            </Box>
          </Grow>
        </Container>

        <Footer />
      </Box>
    </ThemeProvider>
  );
};

export default App;
