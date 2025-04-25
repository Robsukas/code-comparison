import React, { useEffect, useRef, useMemo } from "react";

interface FlowchartRendererProps {
  dsl: string;
  isVisible: boolean;
  drawOptions?: { [key: string]: any };
}

const FlowchartRenderer: React.FC<FlowchartRendererProps> = ({
  dsl,
  isVisible,
  drawOptions = {},
}) => {
  const containerRef   = useRef<HTMLDivElement>(null);
  const containerIdRef = useRef(
    `flowchart-${Math.random().toString(36).slice(2)}`
  );
  const timerRef       = useRef<number | null>(null);

  const memoizedDrawOptions = useMemo(
    () => drawOptions,
    [JSON.stringify(drawOptions)]
  );

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!dsl || !isVisible || !containerRef.current) return;
    if (!(window as any).flowchart) {
      console.error("flowchart.js is not loaded on window!");
      return;
    }

    containerRef.current.innerHTML = "";

    timerRef.current = window.setTimeout(() => {
      try {
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
    }, 200);

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
