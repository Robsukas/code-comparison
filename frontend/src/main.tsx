import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import 'taltech-styleguide/index.css';
import { ConfigProvider } from 'taltech-styleguide';
import './App.css';


createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ConfigProvider locale="et">
      <App />
    </ConfigProvider>
  </StrictMode>,
);
