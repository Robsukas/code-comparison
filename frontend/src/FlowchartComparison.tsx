import React from 'react';
import FlowchartRenderer from './FlowchartRenderer';

interface FlowchartComparisonProps {
  teacherDSL: string;
  studentDSL: string;
}

const FlowchartComparison: React.FC<FlowchartComparisonProps> = ({
  teacherDSL,
  studentDSL,
}) => {
  return (
    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
      <div style={{ flex: '1 1 45%', overflowX: 'auto' }}>
        <h4>Student Flowchart</h4>
        <FlowchartRenderer
          dsl={studentDSL}
          isVisible={true}
          drawOptions={{ scale: 0.7 }}
        />
      </div>

      <div style={{ flex: '1 1 45%', overflowX: 'auto' }}>
        <h4>Teacher Flowchart</h4>
        <FlowchartRenderer
          dsl={teacherDSL}
          isVisible={true}
          drawOptions={{ scale: 0.7 }}
        />
      </div>
    </div>
  );
};

export default FlowchartComparison;
