import React, { useState } from 'react';
import { 
  TTNewButton, 
  Input, 
  Accordion,
  AccordionItem
} from 'taltech-styleguide';
import DropdownSelect from './components/DropdownSelect';
import FlowchartComparison from './FlowchartComparison';
import { CompareCodeResponse, YEARS, EXERCISES } from './types/compareCode';

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

  // Handlers
  const handleSubmit = async () => {
    if (!studentId || !selectedExercise || !selectedYear) {
      setErrorMsg('Please fill in student ID, select an exercise, and select a year');
      return;
    }

    setErrorMsg('');
    setResponseData(null);
    
    try {
      const response = await fetch('http://localhost:5000/api/diff', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId,
          exercise: selectedExercise,
          year: selectedYear
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
    }
  };

  const handleStructuralChange = (funcName: string, isOpen: boolean) => {
    setStructuralOpenMap(prev => ({
      ...prev,
      [funcName]: isOpen,
    }));
  };

  return (
    <div className="compare-code-container">
      <h2>Compare Student Code</h2>

      <div className="inputs-container">
        <div className="input-block">
          <label htmlFor="studentId">Student ID</label>
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

      <TTNewButton onClick={handleSubmit}>Compare</TTNewButton>

      {errorMsg && (
        <div style={{ marginTop: '1rem', color: 'red' }}>
          <strong>Error:</strong> {errorMsg}
        </div>
      )}

      {responseData?.differences && (
        <div style={{ marginTop: '1rem' }}>
          <h3>Module Specific Differences</h3>
          <pre>{JSON.stringify(responseData.differences.module_specific_diffs, null, 2)}</pre>

          <h3>Function Specific Differences</h3>
          <Accordion>
            {Object.entries(responseData.differences.function_specific_diffs).map(
              ([funcName, diffs]) => (
                <AccordionItem key={funcName} itemKey={funcName} label={funcName}>
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
                        <pre>{diffs.strict_comparison.join('\n')}</pre>
                      </AccordionItem>

                      <AccordionItem itemKey="semantic" label="Semantic Comparison">
                        <ul>
                          {diffs.semantic_comparison.map((op: string, idx: number) => (
                            <li key={idx}>{op}</li>
                          ))}
                        </ul>
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
                    </Accordion>
                  </div>
                </AccordionItem>
              )
            )}
          </Accordion>
        </div>
      )}
    </div>
  );
};

export default CompareCode;
