// src/components/ReadmeForm.tsx
import React, { useState, FormEvent } from 'react';

interface ReadmeFormProps {
  onGenerate: (profile: string, repo: string) => Promise<void>;
}

const ReadmeForm: React.FC<ReadmeFormProps> = ({ onGenerate }) => {
  const [profile, setProfile] = useState<string>('');
  const [repo, setRepo] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    await onGenerate(profile, repo);
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
      <div>
        <label htmlFor="profile">GitHub Profile Name:</label>
        <input
          id="profile"
          type="text"
          value={profile}
          onChange={(e) => setProfile(e.target.value)}
          required
          style={{ marginLeft: '10px' }}
        />
      </div>
      <br />
      <div>
        <label htmlFor="repo">Repository Name:</label>
        <input
          id="repo"
          type="text"
          value={repo}
          onChange={(e) => setRepo(e.target.value)}
          required
          style={{ marginLeft: '10px' }}
        />
      </div>
      <br />
      <button type="submit" disabled={loading}>
        {loading ? 'Generating...' : 'Generate README'}
      </button>
    </form>
  );
};

export default ReadmeForm;
