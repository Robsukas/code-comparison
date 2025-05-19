/**
 * Diff View Component
 * 
 * A React component that renders code differences in a side-by-side format using diff2html.
 * The component provides syntax highlighting and synchronized scrolling for better
 * code comparison visualization.
 * 
 * Features:
 * - Side-by-side diff display
 * - Syntax highlighting
 * - Synchronized scrolling
 * - Line-by-line matching
 * 
 * @component
 */

import React, { useEffect, useRef } from 'react';
import { Diff2HtmlUI } from 'diff2html/lib/ui/js/diff2html-ui-slim';

/**
 * Props interface for the DiffView component
 * 
 * @interface DiffViewProps
 * @property {string} diff - The unified diff text to be displayed
 * @property {string} id - Unique identifier for the diff view instance
 */
interface DiffViewProps {
  diff: string;
  id: string;
}

/**
 * DiffView Component
 * 
 * Renders code differences using diff2html with enhanced visualization features.
 * The component uses a ref to manage the diff2html instance and updates
 * when either the diff content or id changes.
 * 
 * Configuration options:
 * - drawFileList: false - Hides the file list for cleaner display
 * - matching: 'lines' - Matches lines for better comparison
 * - outputFormat: 'side-by-side' - Shows differences side by side
 * - synchronisedScroll: true - Enables synchronized scrolling
 * - highlight: true - Enables syntax highlighting
 * 
 * @param {DiffViewProps} props - Component props
 * @returns {JSX.Element} Rendered diff view
 */
const DiffView: React.FC<DiffViewProps> = ({ diff, id }) => {
  // Reference to the container div for diff2html
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current && diff) {
      // Initialize diff2html with configuration
      const diff2htmlUi = new Diff2HtmlUI(
        containerRef.current,
        diff,
        {
          drawFileList: false,      // Hide file list for cleaner display
          matching: 'lines',        // Match lines for better comparison
          outputFormat: 'side-by-side', // Show differences side by side
          synchronisedScroll: true, // Enable synchronized scrolling
          highlight: true          // Enable syntax highlighting
        }
      );
      
      // Render the diff and apply syntax highlighting
      diff2htmlUi.draw();
      diff2htmlUi.highlightCode();
    }
  }, [diff, id]); // Re-render when diff content or id changes

  return <div ref={containerRef} style={{ padding: '1rem' }} />;
};

export default DiffView; 