import React from 'react';
import CompareCode from './CompareCode.tsx';
import './App.css';
import 'diff2html/bundles/css/diff2html.min.css';

const App: React.FC = () => {
  return (
    <div className="App">
      <CompareCode />
    </div>
  );
};

export default App;
