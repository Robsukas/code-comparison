import React, { useState } from 'react';
import { TTNewButton, Input } from 'taltech-styleguide';

interface CompareCodeResponse {
  message?: string;
  strict_ast_result?: any;
  code_diff_result?: string[];
  error?: string;
  details?: string;
}

const CompareCode: React.FC = () => {
  const [codeBlock1, setCodeBlock1] = useState('');
  const [codeBlock2, setCodeBlock2] = useState('');
  const [responseData, setResponseData] = useState<CompareCodeResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async () => {
    setErrorMsg('');
    setResponseData(null);

    try {
      const response = await fetch('http://localhost:5000/api/diff', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code_block_1: codeBlock1,
          code_block_2: codeBlock2,
        }),
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', Array.from(response.headers.entries()));

      const rawText = await response.text();
      console.log('Raw response text:\n', rawText);

      if (!response.ok) {
        setErrorMsg(`HTTP error ${response.status}: ${rawText || 'Unknown error'}`);
      } else {
        try {
          const data: CompareCodeResponse = JSON.parse(rawText);
          setResponseData(data);
        } catch (parseError: any) {
          setErrorMsg(`JSON parse error: ${parseError.message}`);
        }
      }
    } catch (err: any) {
      setErrorMsg(`Error occurred: ${err.message}`);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <h2>Compare Two Code Blocks</h2>

      <div style={{ marginBottom: '1rem' }}>
        <label htmlFor="codeBlock1">Code Block 1</label>
        <Input
          as="textarea"
          id="codeBlock1"
          rows={8}
          value={codeBlock1}
          onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setCodeBlock1(e.target.value)}
        />
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <label htmlFor="codeBlock2">Code Block 2</label>
        <Input
          as="textarea"
          id="codeBlock2"
          rows={8}
          value={codeBlock2}
          onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setCodeBlock2(e.target.value)}
        />
      </div>

      <TTNewButton onClick={handleSubmit}>Compare</TTNewButton>

      {errorMsg && (
        <div style={{ marginTop: '1rem', color: 'red' }}>
          <strong>Error:</strong> {errorMsg}
        </div>
      )}

      {responseData && (
        <pre style={{ marginTop: '1rem', background: '#f4f4f4', padding: '1rem' }}>
          {JSON.stringify(responseData, null, 2)}
        </pre>
      )}
    </div>
  );
};

export default CompareCode;
