import React, { useState, FormEvent } from 'react';
import { LoadingButton } from '@mui/lab';
import { Box, Card, CardContent, TextField, Typography, Fade } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import CodeIcon from '@mui/icons-material/Code';

interface ReadmeFormProps {
  onGenerate: (profile: string, repo: string) => Promise<void>;
}

const ReadmeForm: React.FC<ReadmeFormProps> = ({ onGenerate }) => {
  const [profile, setProfile] = useState('');
  const [repo, setRepo] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    await onGenerate(profile, repo);
    setLoading(false);
  };

  const textFieldSx = {
    width: '80%',
    mx: 'auto',
    '& .MuiOutlinedInput-root': {
      '& fieldset': {
        borderColor: 'white',
        borderWidth: 2,
      },
      '&:hover fieldset': {
        borderColor: 'white',
      },
      '&.Mui-focused fieldset': {
        borderColor: 'white',
      },
    },
  };

  return (
    <Fade in timeout={600}>
      <Card
        sx={{
          maxWidth: 600,
          mx: 'auto',
          my: 4,
          borderRadius: 3,
          bgcolor: 'rgba(30, 30, 30, 0.8)',
          boxShadow: '0 8px 16px rgba(0,0,0,0.3)',
          transition: 'transform 0.3s',
          '&:hover': {
            transform: 'translateY(-5px) rotateX(1deg) rotateY(1deg)',
          },
        }}
      >
        <CardContent>
          <Typography variant="h5" gutterBottom sx={{ textAlign: 'center' }}>
            GitHub Repository Info
          </Typography>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2, textAlign: 'center' }}>
            <TextField
              label="GitHub Profile Name"
              value={profile}
              onChange={(e) => setProfile(e.target.value)}
              margin="normal"
              required
              sx={textFieldSx}
              InputProps={{
                startAdornment: <PersonIcon sx={{ mr: 1 }} />,
              }}
            />
            <TextField
              label="Repository Name"
              value={repo}
              onChange={(e) => setRepo(e.target.value)}
              margin="normal"
              required
              sx={textFieldSx}
              InputProps={{
                startAdornment: <CodeIcon sx={{ mr: 1 }} />,
              }}
            />
            <LoadingButton
              type="submit"
              loading={loading}
              variant="contained"
              size="large"
              sx={{
                width: '80%',
                mt: 3,
                backgroundColor: 'white',
                color: 'black',
                '&:hover': { backgroundColor: '#f5f5f5' },
              }}
            >
              Generate README
            </LoadingButton>
          </Box>
        </CardContent>
      </Card>
    </Fade>
  );
};

export default ReadmeForm;
