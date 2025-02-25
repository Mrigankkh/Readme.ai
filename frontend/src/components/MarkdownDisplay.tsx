import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  Box,
  Divider,
  IconButton,
  Paper,
  Tab,
  Tabs,
  TextField,
  Typography,
  useTheme,
  Tooltip,
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import DownloadIcon from '@mui/icons-material/Download';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

interface MarkdownDisplayProps {
  markdown: string;
}

const MarkdownDisplay: React.FC<MarkdownDisplayProps> = ({ markdown }) => {
  const theme = useTheme();
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    event = event;
    setTabValue(newValue);
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(markdown);
      toast.success('Markdown copied to clipboard!');
    } catch (error) {
      console.error('Failed to copy: ', error);
      toast.error('Failed to copy markdown. Please try again.');
    }
  };

  const handleDownload = () => {
    try {
      const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'README.md';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      toast.success('Markdown downloaded as README.md');
    } catch (error) {
      console.error('Failed to download: ', error);
      toast.error('Failed to download markdown. Please try again.');
    }
  };

  return (
    <Box sx={{ mt: 4, width: '100%' }}>
      <Divider sx={{ my: 4 }} />
      <Typography variant="h4" gutterBottom sx={{ textAlign: 'center', color: 'white' }}>
        Generated README
      </Typography>
      <Tabs
        value={tabValue}
        onChange={handleTabChange}
        centered
        textColor="inherit"
        indicatorColor="secondary"
        sx={{
          color: 'white',
          '& .MuiTab-root': { fontSize: '1.2rem' },
        }}
      >
        <Tab label="Raw Markdown" sx={{ color: 'white', fontSize: '1.2rem' }} />
        <Tab label="Preview" sx={{ color: 'white', fontSize: '1.2rem' }} />
      </Tabs>
      {tabValue === 0 && (
        <Paper
          sx={{
            p: 2,
            bgcolor: 'background.paper',
            mt: 2,
            borderRadius: 2,
            boxShadow: 3,
            width: '100%',
            position: 'relative',
          }}
        >
          <Tooltip title="Download Markdown">
            <IconButton
              onClick={handleDownload}
              sx={{
                position: 'absolute',
                top: 8,
                right: 60,
                color: 'white',
                backgroundColor: 'transparent',
                '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.3)' },
                width: 48,
                height: 48,
                zIndex: 2,
              }}
            >
              <DownloadIcon sx={{ fontSize: 28 }} />
            </IconButton>
          </Tooltip>
          <Tooltip title="Copy Markdown">
            <IconButton
              onClick={handleCopy}
              sx={{
                position: 'absolute',
                top: 8,
                right: 8,
                color: 'white',
                backgroundColor: 'transparent',
                '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.3)' },
                width: 48,
                height: 48,
                zIndex: 2,
              }}
            >
              <ContentCopyIcon sx={{ fontSize: 28 }} />
            </IconButton>
          </Tooltip>
          <TextField
            fullWidth
            multiline
            value={markdown}
            variant="outlined"
            InputProps={{
              readOnly: true,
              sx: {
                fontFamily: 'monospace',
                fontSize: '0.875rem',
                '& textarea': {
                  resize: 'vertical',
                  paddingTop: '48px', // extra padding to prevent overlap with buttons
                },
              },
            }}
          />
        </Paper>
      )}
      {tabValue === 1 && (
        <Paper
          sx={{
            p: 2,
            bgcolor: 'background.paper',
            mt: 2,
            borderRadius: 2,
            boxShadow: 3,
            width: '100%',
            '& pre': {
              backgroundColor: theme.palette.mode === 'dark' ? '#1e1e1e' : '#f5f5f5',
              p: 2,
              pt: '48px', // extra top padding to prevent overlap with buttons
              borderRadius: 1,
            },
          }}
        >
          <ReactMarkdown>{markdown}</ReactMarkdown>
        </Paper>
      )}
      <ToastContainer 
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        pauseOnHover
      />
    </Box>
  );
};

export default MarkdownDisplay;
