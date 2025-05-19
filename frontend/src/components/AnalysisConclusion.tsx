/**
 * Analysis Conclusion Component
 * 
 * A React component that displays AI-generated code analysis conclusions in a structured format.
 * The component parses and formats different sections of the analysis, including:
 * - Function analysis sections
 * - Status indicators (OK/ISSUES)
 * - Recommendations and issues
 * - Final conclusions
 * 
 * The component uses the Taltech Styleguide for consistent styling and typography.
 * 
 * @component
 */

import React from 'react';
import { Typography, Separator, Tag } from 'taltech-styleguide';

/**
 * Props interface for the AnalysisConclusion component
 * 
 * @interface AnalysisConclusionProps
 * @property {string} conclusion - The AI-generated analysis text to be displayed
 * @property {string | null} [llmModel] - Optional name of the LLM model used for analysis
 */
interface AnalysisConclusionProps {
  conclusion: string;
  llmModel?: string | null;
}

/**
 * AnalysisConclusion Component
 * 
 * Renders AI analysis conclusions with formatted sections and styling.
 * The component processes the conclusion text to identify and format:
 * - Section headers (FUNCTION ANALYSIS, FINAL CONCLUSION)
 * - Function names (prefixed with #)
 * - Status indicators (OK/ISSUES)
 * - Recommendations and issues
 * 
 * @param {AnalysisConclusionProps} props - Component props
 * @returns {JSX.Element} Formatted analysis conclusion display
 */
const AnalysisConclusion: React.FC<AnalysisConclusionProps> = ({ conclusion, llmModel }) => {
  // Split the text into sections for processing
  const sections = conclusion.split('\n\n');
  
  return (
    <div style={{ whiteSpace: 'pre-wrap' }}>
      {/* Header section with AI Analysis and Model tags */}
      <div
        style={{
          display: 'flex',
          gap: '0.5rem',      // distance between the chips
          marginBottom: '1rem',
          alignItems: 'center',
        }}
      >
        <Tag text="Experimental AI Analysis" variant="danger-filled" size="md" />
        
        {llmModel && (
          <Tag text={llmModel} variant="info-filled" size="md" />
        )}
      </div>

      {/* Process and render each section */}
      {sections.map((section, sectionIndex) => {
        // Process each line within the section
        const processedLines = section.split('\n').map((line, lineIndex) => {
          // Handle section headers (FUNCTION ANALYSIS, FINAL CONCLUSION)
          if (line === 'FUNCTION ANALYSIS:' || line === 'FINAL CONCLUSION:') {
            return (
              <Typography key={lineIndex} as="h4" visual="h4" modifiers={[]}>
                {line}
              </Typography>
            );
          }
          
          // Handle function names (prefixed with #)
          if (line.trim().startsWith('#')) {
            const functionName = line.trim().substring(1); // Remove the # prefix
            return (
              <Typography key={lineIndex} as="h5" visual="h5" modifiers={[]}>
                {functionName}
              </Typography>
            );
          }
          
          // Handle status lines with color-coded indicators
          if (line.includes('Status:')) {
            const parts = line.split(':');
            const status = parts[1].trim();
            return (
              <Typography key={lineIndex} as="p" visual="body" modifiers={[]}>
                Status:{' '}
                <Typography 
                  as="span" 
                  visual="h5"
                  color={status === 'OK' ? 'success' : 'danger'}
                  modifiers={[]}
                >
                  {status}
                </Typography>
              </Typography>
            );
          }
          
          // Handle recommendations and issues with special formatting
          if (line.includes('Recommendations:') || line.includes('Issues:')) {
            const parts = line.split(':');
            const type = parts[0].trim();
            const content = parts[1].trim();
            return (
              <Typography key={lineIndex} as="p" visual="body" modifiers={[]}>
                {type}:{' '}
                {content === 'None' ? (
                  <Typography as="span" visual="body" color="success" modifiers={[]}>
                    None
                  </Typography>
                ) : (
                  <Typography as="span" visual="body" modifiers={[]}>
                    {content}
                  </Typography>
                )}
              </Typography>
            );
          }
          
          // Default case - regular text with standard formatting
          return (
            <Typography key={lineIndex} as="p" visual="body" modifiers={[]}>
              {line}
            </Typography>
          );
        });

        return (
          <React.Fragment key={sectionIndex}>
            {processedLines}
            {sectionIndex < sections.length - 1 && <Separator />}
          </React.Fragment>
        );
      })}
    </div>
  );
};

export default AnalysisConclusion; 