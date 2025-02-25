import React from 'react';
import { Box, Container, Link, Typography } from '@mui/material';

const Footer: React.FC = () => {
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        backgroundColor: 'transparent',
      }}
    >
      <Container maxWidth="sm" sx={{ textAlign: 'center' }}>
        <Typography variant="body1" sx={{ color: 'inherit' }}>
          © {new Date().getFullYear()} Mrigank Khandelwal
        </Typography>
        <Typography variant="body2">
          <Link href="https://github.com/Mrigankkh" target="_blank" rel="noopener" sx={{ color: 'inherit', textDecoration: 'none' }}>
            GitHub
          </Link>{' '}
          |{' '}
          <Link href="https:/mrigank.me" target="_blank" rel="noopener" sx={{ color: 'inherit', textDecoration: 'none' }}>
            Personal Website
          </Link>
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer;
