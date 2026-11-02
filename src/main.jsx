import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import WidgetApp from './WidgetApp.jsx';
import './index.css';
import './widget.css';
import './widget-preview.css';

const isWidgetRoute = window.location.pathname === '/widget';
const isStandaloneSupportRoute = window.location.pathname === '/';
document.body.classList.toggle('widget-page', isWidgetRoute);
document.documentElement.classList.toggle('widget-html', isWidgetRoute);
document.body.classList.toggle('support-preview-page', isWidgetRoute || isStandaloneSupportRoute);
document.documentElement.classList.toggle('support-preview-html', isWidgetRoute || isStandaloneSupportRoute);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    {isWidgetRoute ? (
      <WidgetApp />
    ) : isStandaloneSupportRoute ? (
      <WidgetApp standalone />
    ) : (
      <App />
    )}
  </StrictMode>
);
