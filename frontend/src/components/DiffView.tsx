import React, { useEffect, useRef } from 'react';
import { Diff2HtmlUI } from 'diff2html/lib/ui/js/diff2html-ui-slim';

interface DiffViewProps {
  diff: string;
  id: string;
}

const DiffView: React.FC<DiffViewProps> = ({ diff, id }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current && diff) {
      const diff2htmlUi = new Diff2HtmlUI(
        containerRef.current,
        diff,
        {
          drawFileList: false,
          matching: 'lines',
          outputFormat: 'side-by-side',
          synchronisedScroll: true,
          highlight: true
        }
      );
      diff2htmlUi.draw();
      diff2htmlUi.highlightCode();
    }
  }, [diff, id]);

  return <div ref={containerRef} style={{ padding: '1rem' }} />;
};

export default DiffView; 