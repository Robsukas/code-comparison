import React from "react";
import FlowchartRenderer from "./FlowchartRenderer";
import { Typography } from "taltech-styleguide";

interface FlowchartComparisonProps {
  unifiedDSL: string;
  structural_error?: string | null;
}

const Legend = () => (
  <div style={{ display: "flex", gap: "1.5rem", margin: "0.5rem 0" }}>
    <LegendSwatch color="#cce5ff" label="only in teacher code" />
    <LegendSwatch color="#f5c2c2" label="only in student code" />
    <LegendSwatch color="#ffd17c" label="Δ big diff" />
    <LegendSwatch color="#ffffb3" label="✎ small edit" />
  </div>
);

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
