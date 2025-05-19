/**
 * Flowchart Renderer Component
 * 
 * A React component that renders flowcharts using the flowchart.js library.
 * It supports:
 * - DSL (Domain Specific Language) parsing
 * - SVG rendering
 * - Custom styling and scaling
 * - Difference highlighting
 * - Debounced rendering
 * 
 * The component uses refs to manage DOM elements and timers, and includes
 * cleanup logic to prevent memory leaks.
 * 
 * @component
 */

import React, { useEffect, useRef, useMemo } from "react";

/**
 * Props interface for the FlowchartRenderer component
 * 
 * @interface FlowchartRendererProps
 * @property {string} dsl - Flowchart DSL string to be rendered
 * @property {boolean} isVisible - Whether the flowchart should be visible
 * @property {Object} [drawOptions] - Optional rendering configuration
 * @property {number} [drawOptions.scale] - Scale factor for the flowchart
 * @property {Object} [drawOptions.flowstate] - Custom styling for different states
 */
interface FlowchartRendererProps {
  dsl: string;
  isVisible: boolean;
  drawOptions?: { [key: string]: any };
}

/**
 * FlowchartRenderer Component
 * 
 * Renders a flowchart from DSL with support for difference highlighting
 * and custom styling. Uses a debounced rendering approach to prevent
 * excessive re-renders.
 * 
 * Color coding for differences:
 * - Blue (#cce5ff): Code only in teacher's solution
 * - Red (#f5c2c2): Code only in student's solution
 * - Orange (#ffd17c): Major differences (Δ)
 * - Yellow (#ffffb3): Minor differences (✎)
 * 
 * @param {FlowchartRendererProps} props - Component props
 * @returns {JSX.Element} Container div for the flowchart
 */
const FlowchartRenderer: React.FC<FlowchartRendererProps> = ({
  dsl,
  isVisible,
  drawOptions = {},
}) => {
  // Reference to the container div element
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Generate a unique ID for the flowchart container
  const containerIdRef = useRef(
    `flowchart-${Math.random().toString(36).slice(2)}`
  );
  
  // Reference for the debounce timer
  const timerRef = useRef<number | null>(null);

  // Memoize draw options to prevent unnecessary re-renders
  const memoizedDrawOptions = useMemo(
    () => drawOptions,
    [JSON.stringify(drawOptions)]
  );

  // Cleanup timer on component unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, []);

  // Main rendering effect
  useEffect(() => {
    // Skip rendering if conditions aren't met
    if (!dsl || !isVisible || !containerRef.current) return;
    
    // Check if flowchart.js is available
    if (!(window as any).flowchart) {
      console.error("flowchart.js is not loaded on window!");
      return;
    }

    // Clear previous content
    containerRef.current.innerHTML = "";

    // Debounce the rendering to prevent excessive updates
    timerRef.current = window.setTimeout(() => {
      try {
        // Parse DSL and render SVG
        const chart = (window as any).flowchart.parse(dsl);
        chart.drawSVG(containerIdRef.current, {
          scale: memoizedDrawOptions.scale || 1,
          flowstate: {
            diff_teacher_only: { fill: "#cce5ff" }, // blue
            diff_student_only: { fill: "#f5c2c2" }, // red
            diff_replace:      { fill: "#ffd17c" }, // orange (Δ big diff)
            diff_edit:         { fill: "#ffffb3" }, // yellow (✎ small edit)
          },
          ...memoizedDrawOptions,
        });
      } catch (error) {
        console.error("Error rendering flowchart:", error);
      }
    }, 200); // 200ms debounce delay

    // Cleanup timer on effect cleanup
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [dsl, isVisible, memoizedDrawOptions]);

  return (
    <div
      ref={containerRef}
      id={containerIdRef.current}
      style={{ width: "100%", minHeight: "300px", overflowX: "auto" }}
    />
  );
};

export default FlowchartRenderer;
