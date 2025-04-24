import React, { useState } from 'react';
import { 
  TTNewButton, 
  Input, 
  Accordion,
  AccordionItem,
  TTNewCard,
  TTNewCardContent,
  Heading,
  Typography,
  FilterBar,
  Loader
} from 'taltech-styleguide';
import DropdownSelect from './components/DropdownSelect';
import FlowchartComparison from './FlowchartComparison';
import { CompareCodeResponse, YEARS, EXERCISES } from './types/compareCode';
import AnalysisConclusion from './components/AnalysisConclusion';
import DiffView from './components/DiffView';
import './styles/ComparisonView.css';

const CompareCode: React.FC = () => {
  // State
  const [studentId, setStudentId] = useState('');
  const [selectedExercise, setSelectedExercise] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [responseData, setResponseData] = useState<CompareCodeResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [structuralOpenMap, setStructuralOpenMap] = useState<{ [funcName: string]: boolean }>({});
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isYearDropdownOpen, setIsYearDropdownOpen] = useState(false);
  const [useLLM, setUseLLM] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  // Filter options
  const filterOptions = [
    {
      color: '#51BFD3',
      label: 'AI Analysis',
      value: 'llm'
    }
  ];

  // Handlers
  const handleSubmit = async () => {
    if (!studentId || !selectedExercise || !selectedYear) {
      setErrorMsg('Please fill in student ID, select an exercise, and select a year');
      return;
    }

    setErrorMsg('');
    setResponseData(null);
    setIsLoading(true);
    
    try {
      const response = await fetch('http://localhost:5000/api/diff', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId,
          exercise: selectedExercise,
          year: selectedYear,
          use_llm: useLLM
        }),
      });
      
      const rawText = await response.text();

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
    } finally {
      setIsLoading(false);
    }
  };

  const handleStructuralChange = (funcName: string, isOpen: boolean) => {
    setStructuralOpenMap(prev => ({
      ...prev,
      [funcName]: isOpen,
    }));
  };

  const handleFilterChange = (values: any[]) => {
    setUseLLM(values.some(value => value.value === 'llm'));
  };

  return (
    <div className="compare-code-container">
      <Heading as="h2" visual="h2" color="primary">Compare Student Code</Heading>

      <div className="inputs-container">
        <div className="input-block">
          <label htmlFor="studentId">
            <Typography as="span" visual="label">Student ID</Typography>
          </label>
          <Input
            id="studentId"
            value={studentId}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setStudentId(e.target.value)
            }
            placeholder="Enter student ID"
          />
        </div>

        <DropdownSelect
          id="yearSelect"
          label="Year"
          options={YEARS}
          selectedValue={selectedYear}
          onSelect={setSelectedYear}
          isOpen={isYearDropdownOpen}
          setIsOpen={setIsYearDropdownOpen}
        />

        <DropdownSelect
          id="exerciseSelect"
          label="Exercise"
          options={EXERCISES}
          selectedValue={selectedExercise}
          onSelect={setSelectedExercise}
          isOpen={isDropdownOpen}
          setIsOpen={setIsDropdownOpen}
        />
      </div>

      <div style={{ margin: '1rem 0' }}>
        <FilterBar
          options={filterOptions}
          values={useLLM ? filterOptions : []}
          onChange={handleFilterChange}
          size="sm"
          allToggle="All filters"
        />
      </div>

      <TTNewButton onClick={handleSubmit}>Compare</TTNewButton>

      {errorMsg && (
        <div style={{ marginTop: '1rem' }}>
          <Typography as="p" color="danger">
            <Typography as="strong">Error:</Typography> {errorMsg}
          </Typography>
        </div>
      )}

      {isLoading && (
        <div style={{ margin: '2rem 0' }}>
          <Loader size="lg" center overlay />
        </div>
      )}

      {responseData && !isLoading && (
        <div style={{ marginTop: '2rem' }}>
          {responseData.conclusion && (
            <div style={{ marginBottom: '2rem' }}>
              <TTNewCard>
                <TTNewCardContent>
                  <AnalysisConclusion conclusion={responseData.conclusion} />
                </TTNewCardContent>
              </TTNewCard>
            </div>
          )}

          {responseData.differences && (
            <>
              {responseData.differences.module_specific_diffs.function_mismatch.length > 0 && (
                <>
                  <div>
                    <Heading as="h3" visual="h3" color="primary">
                      Module Specific Differences
                    </Heading>
                  </div>
                  <div style={{ marginBottom: '2rem' }}>
                    <TTNewCard>
                      <TTNewCardContent>
                        <ul className="comparison-list">
                          {responseData.differences.module_specific_diffs.function_mismatch.map((mismatch, idx) => (
                            <li key={idx} className="comparison-list-item">
                              <Typography as="span" color="danger" visual="h5">
                                {mismatch}
                              </Typography>
                            </li>
                          ))}
                        </ul>
                      </TTNewCardContent>
                    </TTNewCard>
                  </div>
                </>
              )}

              <div style={{ marginBottom: '1rem' }}>
                <Heading as="h3" visual="h3" color="primary">
                  Function Specific Differences
                </Heading>
              </div>
              <Accordion>
                {Object.entries(responseData.differences.function_specific_diffs).map(
                  ([filename, fileDiffs]) => (
                    <AccordionItem key={filename} itemKey={filename} label={filename}>
                      <Accordion>
                        {Object.entries(fileDiffs).map(
                          ([funcName, diffs]) => (
                            <AccordionItem key={funcName} itemKey={`${filename}-${funcName}`} label={funcName}>
                              <div style={{ padding: '1rem' }}>
                                <Accordion
                                  onChange={(key, state) => {
                                    if (key === 'structural') {
                                      handleStructuralChange(funcName, state === 'open');
                                    }
                                  }}
                                  defaultItemKey=""
                                >
                                  <AccordionItem itemKey="strict" label="Strict Comparison">
                                    <TTNewCard>
                                      <TTNewCardContent>
                                        <ul className="comparison-list">
                                          {diffs.strict_comparison.map((line: string, idx: number) => (
                                            <li key={idx} className="comparison-list-item">{line}</li>
                                          ))}
                                        </ul>
                                      </TTNewCardContent>
                                    </TTNewCard>
                                  </AccordionItem>

                                  <AccordionItem 
                                    itemKey="structural" 
                                    label="Structural Comparison"
                                  >
                                    {structuralOpenMap[funcName] && (
                                      <FlowchartComparison
                                        teacherDSL={diffs.teacherDSL}
                                        studentDSL={diffs.studentDSL}
                                      />
                                    )}
                                  </AccordionItem>

                                  <AccordionItem 
                                    itemKey="diff" 
                                    label="Diff View"
                                  >
                                    {diffs.unified_diff && (
                                      <DiffView 
                                        diff={diffs.unified_diff}
                                        id={`diff-${filename}-${funcName}`}
                                      />
                                    )}
                                  </AccordionItem>
                                </Accordion>
                              </div>
                            </AccordionItem>
                          )
                        )}
                      </Accordion>
                    </AccordionItem>
                  )
                )}
              </Accordion>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default CompareCode;
