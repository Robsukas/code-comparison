import React from 'react';
import { Typography, Separator, Tag } from 'taltech-styleguide';

interface AnalysisConclusionProps {
  conclusion: string;
}

const AnalysisConclusion: React.FC<AnalysisConclusionProps> = ({ conclusion }) => {
  // Split the text into sections
  const sections = conclusion.split('\n\n');
  
  return (
    <div style={{ whiteSpace: 'pre-wrap' }}>
      <div style={{ marginBottom: '1rem' }}>
        <Tag 
          text="Experimental AI Analysis" 
          variant="danger-filled"
          size="md"
        />
      </div>
      {sections.map((section, sectionIndex) => {
        // Process each line within the section
        const processedLines = section.split('\n').map((line, lineIndex) => {
          // Handle section headers
          if (line === 'FUNCTION ANALYSIS:' || line === 'FINAL CONCLUSION:') {
            return (
              <Typography key={lineIndex} as="h4" visual="h4" modifiers={[]}>
                {line}
              </Typography>
            );
          }
          
          // Handle function names (fn(some_function))
          if (line.trim().startsWith('fn(')) {
            return (
              <Typography key={lineIndex} as="h5" visual="h5" modifiers={[]}>
                {line}
              </Typography>
            );
          }
          
          // Handle status lines - only highlight OK/ISSUES
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
          
          // Handle recommendations and issues lines
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
          
          // Default case - regular text
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