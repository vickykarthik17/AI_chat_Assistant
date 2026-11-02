import SupportChatWidget from './components/SupportChatWidget.jsx';

const supportApiUrl = (import.meta.env.VITE_SUPPORT_API_URL || '/api').replace(
  /\/+$/,
  '',
);
const isStandalonePreview = window.location.pathname === '/';
const isEmbeddedPreview =
  new URLSearchParams(window.location.search).get('embedded') === '1';

export default function WidgetApp() {
  return (
    <SupportChatWidget
      apiUrl={supportApiUrl}
      mode={isStandalonePreview ? 'standalone' : 'widget'}
      initialOpen={isStandalonePreview || isEmbeddedPreview}
    />
  );
}
