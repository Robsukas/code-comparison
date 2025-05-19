/**
 * Flowchart Comparison Component
 * 
 * A React component that visualizes differences between student and teacher code
 * using flowcharts. It includes a color-coded legend to help understand the
 * different types of differences shown in the flowchart.
 * 
 * Features:
 * - Color-coded difference visualization
 * - Interactive legend
 * - Error handling
 * - Scaled flowchart rendering
 * 
 * @component
 */

import React from "react";
import FlowchartRenderer from "./FlowchartRenderer";
import { Typography } from "taltech-styleguide";

/**
 * Props interface for the FlowchartComparison component
 * 
 * @interface FlowchartComparisonProps
 * @property {string} unifiedDSL - The unified flowchart DSL containing both student and teacher code
 * @property {string | null} [structural_error] - Optional error message from structural comparison
 */
interface FlowchartComparisonProps {
  unifiedDSL: string;
  structural_error?: string | null;
}

/**
 * Legend Component
 * 
 * Displays a color-coded legend explaining the different types of differences
 * shown in the flowchart:
 * - Blue: Code only in teacher's solution
 * - Red: Code only in student's solution
 * - Orange: Major differences (marked with Δ)
 * - Yellow: Minor differences (marked with ✎)
 * 
 * @returns {JSX.Element} Color-coded legend with explanations
 */
const Legend = () => (
  <div style={{ display: "flex", gap: "1.5rem", margin: "0.5rem 0" }}>
    <LegendSwatch color="#cce5ff" label="only in teacher code" />
    <LegendSwatch color="#f5c2c2" label="only in student code" />
    <LegendSwatch color="#ffd17c" label="Δ big diff" />
    <LegendSwatch color="#ffffb3" label="✎ small edit" />
  </div>
);

/**
 * Legend Swatch Component
 * 
 * Renders a single color swatch with its label in the legend.
 * 
 * @param {Object} props - Component props
 * @param {string} props.color - CSS color value for the swatch
 * @param {string} props.label - Text label for the swatch
 * @returns {JSX.Element} Color swatch with label
 */
const LegendSwatch = ({ color, label }: { color: string; label: string }) => (
  <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
    <span
      style={{
        display: "inline-block",
        width: "1rem",
        height: "1rem",
        background: color,
        border: "1px solid #777",
      }}
    />
    <Typography as="span" visual="label">
      {label}
    </Typography>
  </div>
);

/**
 * FlowchartComparison Component
 * 
 * Main component that renders either:
 * - An error message if structural_error is present
 * - A flowchart visualization with legend if no errors
 * 
 * The flowchart is rendered at 70% scale for better visibility.
 * 
 * @param {FlowchartComparisonProps} props - Component props
 * @returns {JSX.Element} Either error message or flowchart with legend
 */
const FlowchartComparison: React.FC<FlowchartComparisonProps> = ({
  unifiedDSL,
  structural_error,
}) => {
  if (structural_error) {
    return <p style={{ color: "red" }}>{structural_error}</p>;
  }

  return (
    <>
      <Legend />

      <FlowchartRenderer
        dsl={unifiedDSL}
        isVisible={true}
        drawOptions={{ scale: 0.7 }}
      />
    </>
  );
};

export default FlowchartComparison;
