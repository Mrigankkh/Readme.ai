// src/components/MarkdownDisplay.tsx
import React from 'react';
import ReactMarkdown from 'react-markdown';

interface MarkdownDisplayProps {
  markdown: string;
}

const MarkdownDisplay: React.FC<MarkdownDisplayProps> = ({ markdown }) => {
  return (
    <div>
      <hr />
      <h2>Generated README</h2>
      <div style={{ display: 'flex', gap: '20px' }}>
        <div style={{ flex: 1 }}>
          <h3>Raw Markdown</h3>
          <textarea
            style={{
              width: '100%',
              height: '400px',
              padding: '10px',
              fontFamily: 'monospace',
              fontSize: '14px'
            }}
            readOnly
            value={markdown}
          />
        </div>
        <div style={{ flex: 1 }}>
          <h3>Markdown Preview</h3>
          <div
            style={{
              border: '1px solid #ccc',
              padding: '10px',
              height: '400px',
              overflowY: 'auto'
            }}
          >
            <ReactMarkdown>{markdown}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarkdownDisplay;
