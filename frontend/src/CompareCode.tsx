import React, { useState } from 'react';
import { TTNewButton, Input, Accordion, AccordionItem } from 'taltech-styleguide';
import FlowchartComparison from './FlowchartComparison';

interface FunctionDiffs {
  strict_comparison: string[];
  code_diff: string[];
  teacherDSL: string;
  studentDSL: string;
  diffMetadata: {
    extraInStudent: string[];
    extraInTeacher: string[];
  };
}

interface ModuleSpecificDiffs {
  function_mismatch: string[];
}

interface Differences {
  module_specific_diffs: ModuleSpecificDiffs;
  function_specific_diffs: { [key: string]: FunctionDiffs };
}

interface CompareCodeResponse {
  message?: string;
  differences?: Differences;
  error?: string;
  details?: string;
}

const CompareCode: React.FC = () => {
  const [studentCodeBlock, setStudentCodeBlock] = useState('');
  const [checkCodeBlock, setCheckCodeBlock] = useState('');
  const [responseData, setResponseData] = useState<CompareCodeResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [structuralOpenMap, setStructuralOpenMap] = useState<{ [funcName: string]: boolean }>({});

  const handleSubmit = async () => {
    setErrorMsg('');
    setResponseData(null);
    try {
      const response = await fetch('http://localhost:5000/api/diff', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_code_block: studentCodeBlock,
          check_code_block: checkCodeBlock,
        }),
      });
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
    <div className="compare-code-container">
      <h2>Compare Two Code Blocks</h2>

      <div className="inputs-container">
        <div className="code-input-block">
          <label htmlFor="studentCodeBlock">Student Code Block</label>
          <Input
            as="textarea"
            id="studentCodeBlock"
            rows={12}
            value={studentCodeBlock}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
              setStudentCodeBlock(e.target.value)
            }
          />
        </div>

        <div className="code-input-block">
          <label htmlFor="checkCodeBlock">Teacher Code Block</label>
          <Input
            as="textarea"
            id="checkCodeBlock"
            rows={12}
            value={checkCodeBlock}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
              setCheckCodeBlock(e.target.value)
            }
          />
        </div>
      </div>

      <TTNewButton onClick={handleSubmit}>Compare</TTNewButton>

      {errorMsg && (
        <div style={{ marginTop: '1rem', color: 'red' }}>
          <strong>Error:</strong> {errorMsg}
        </div>
      )}

      {responseData && responseData.differences && (
        <div style={{ marginTop: '1rem' }}>
          <h3>Module Specific Differences</h3>
          <pre>{JSON.stringify(responseData.differences.module_specific_diffs, null, 2)}</pre>

          <h3>Function Specific Differences</h3>
          <Accordion>
            {Object.entries(responseData.differences.function_specific_diffs).map(
              ([funcName, diffs]) => {
                const isOpen = structuralOpenMap[funcName] || false;
                return (
                  <AccordionItem key={funcName} itemKey={funcName} label={funcName}>
                    <div style={{ padding: '1rem' }}>
                      <Accordion
                        onChange={(key: string, state: 'close' | 'open') => {
                          if (key === 'structural') {
                            setStructuralOpenMap((prev) => ({
                              ...prev,
                              [funcName]: state === 'open',
                            }));
                          }
                        }}
                        defaultItemKey=""
                      >
                        <AccordionItem itemKey="strict" label="Strict Comparison">
                          <pre>{diffs.strict_comparison.join('\n')}</pre>
                        </AccordionItem>

                        <AccordionItem itemKey="code" label="Code Diff">
                          <pre>{diffs.code_diff.join('\n')}</pre>
                        </AccordionItem>

                        <AccordionItem itemKey="structural" label="Structural Comparison">
                          {isOpen && (
                            <FlowchartComparison
                              teacherDSL={diffs.teacherDSL}
                              studentDSL={diffs.studentDSL}
                            />
                          )}
                        </AccordionItem>
                      </Accordion>
                    </div>
                  </AccordionItem>
                );
              }
            )}
          </Accordion>
        </div>
      )}
    </div>
  );
};

export default CompareCode;
