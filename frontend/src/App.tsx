// src/App.tsx
import React, { useState } from 'react';
import ReadmeForm from './components/ReadmeForm';
import MarkdownDisplay from './components/MarkdownDisplay';

const App: React.FC = () => {
  
  const BACKEND_SERVER = import.meta.env.BACKEND_URL || 'readme.mrigank.me'; // Adjust this to your backend server address

  const [markdownResult, setMarkdownResult] = useState<string>('');

  const handleGenerate = async (profile: string, repo: string) => {
    try {
      const formData = new FormData();
      formData.append('profile', profile);
      formData.append('repo', repo);

      // Adjust the URL to your Flask backend endpoint if necessary.
      const response = await fetch(`https://${BACKEND_SERVER}/generate-readme`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.statusText}`);
      }

      const data = await response.json();
      setMarkdownResult(data.readme);
    } catch (error: any) {
      console.error('Error generating README:', error);
      alert(`Error: ${error.message}`);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>README Generator</h1>
      <ReadmeForm onGenerate={handleGenerate} />
      {markdownResult && <MarkdownDisplay markdown={markdownResult} />}
    </div>
  );
};

export default App;
