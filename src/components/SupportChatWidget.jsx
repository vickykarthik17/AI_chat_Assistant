import { useEffect, useId, useRef, useState } from 'react';
import { ArrowDown, ArrowUp, Headset, MessageCircle, X } from 'lucide-react';

const welcomeMessage = {
  id: 'welcome',
  role: 'assistant',
  content: "Hi! I’m here to help you with Sadhana Mythri. What would you like help with?",
};

const suggestedQuestions = [
  { label: 'Explore plans', message: 'What plans do you offer?' },
  { label: 'Get started', message: 'How do I get started?' },
  { label: 'Contact support', message: 'How can I contact support?' },
];

export default function SupportChatWidget({
  apiUrl = '/api',
  title = 'Sadhana Mythri',
  mode = 'widget',
  initialOpen = false,
  showLauncher = true,
}) {
  const [isOpen, setIsOpen] = useState(initialOpen);
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState([welcomeMessage]);
  const inputRef = useRef(null);
  const messagesRef = useRef(null);
  const inputId = useId();
  const titleId = useId();
  const supportApiUrl = apiUrl.replace(/\/+$/, '');
  const isStandalone = mode === 'standalone';

  useEffect(() => {
    const handleOpenWidget = () => setIsOpen(true);
    window.addEventListener('sadhana-support-widget:open', handleOpenWidget);
    return () =>
      window.removeEventListener('sadhana-support-widget:open', handleOpenWidget);
  }, []);

  useEffect(() => {
    if (isOpen) inputRef.current?.focus();
  }, [isOpen]);

  useEffect(() => {
    messagesRef.current?.scrollTo({
      top: messagesRef.current.scrollHeight,
      behavior: 'smooth',
    });
  }, [messages, isOpen]);

  useEffect(() => {
    if (!isOpen) return undefined;
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') setIsOpen(false);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  async function sendMessage(content) {
    const trimmedContent = content.trim();
    if (!trimmedContent || isSending) return;

    const history = messages
      .filter((item) => item.role === 'user')
      .slice(-2)
      .map(({ role, content: previousContent }) => ({
        role,
        content: previousContent,
      }));
    setMessages((current) => [
      ...current,
      { id: crypto.randomUUID(), role: 'user', content: trimmedContent },
    ]);
    setMessage('');
    setIsSending(true);
    setIsTyping(true);
    const assistantId = crypto.randomUUID();

    try {
      const response = await fetch(`${supportApiUrl}/support/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmedContent, history }),
      });
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || 'The support assistant is unavailable.');
      }
      if (!response.body) {
        throw new Error('The support assistant returned an empty response.');
      }
      setMessages((current) => [
        ...current,
        { id: assistantId, role: 'assistant', content: '' },
      ]);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let hasReceivedText = false;
      let streamComplete = false;
      const handleEvent = (eventText) => {
        const data = eventText
          .split(/\r?\n/)
          .filter((line) => line.startsWith('data:'))
          .map((line) => line.slice(5).trim())
          .join('\n');
        if (!data) return;

        const event = JSON.parse(data);
        if (event.error) throw new Error(event.error);
        if (event.stop) {
          streamComplete = true;
          return;
        }
        if (typeof event.text === 'string' && event.text) {
          hasReceivedText = true;
          setIsTyping(false);
          setMessages((current) =>
            current.map((item) =>
              item.id === assistantId
                ? { ...item, content: item.content + event.text }
                : item,
            ),
          );
        }
      };

      while (!streamComplete) {
        const { done, value } = await reader.read();
        buffer += decoder.decode(value, { stream: !done });
        const events = buffer.split(/\r?\n\r?\n/);
        buffer = events.pop() || '';
        for (const eventText of events) {
          handleEvent(eventText);
          if (streamComplete) break;
        }
        if (done) break;
      }
      if (!streamComplete && buffer.trim()) handleEvent(buffer);
      if (streamComplete) await reader.cancel();
      if (!streamComplete) {
        throw new Error('The support assistant response ended before completion.');
      }
      if (!hasReceivedText) {
        throw new Error('The support assistant returned an empty response.');
      }
    } catch (error) {
      console.error('Support chat request failed:', error);
      setMessages((current) => [
        ...current.filter((item) => item.id !== assistantId),
        {
          id: assistantId,
          role: 'assistant',
          content:
            'Sorry, support chat is temporarily unavailable. Please try again or contact +91 8904178434 or info@we-hive.com.',
        },
      ]);
    } finally {
      setIsSending(false);
      setIsTyping(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    void sendMessage(message);
  }

  return (
    <main
      className={`support-widget-root${isStandalone ? ' is-standalone' : ''}`}
      aria-label={`${title} support chat`}
    >
      {isOpen && (
        <section
          className="support-widget-panel"
          role="dialog"
          aria-modal="false"
          aria-labelledby={titleId}
        >
          <header className="support-widget-header">
            <div className="support-widget-brand">
              <span className="support-widget-avatar" aria-hidden="true">
                <Headset size={20} strokeWidth={1.8} />
              </span>
              <div>
                <h1 id={titleId}>{title}</h1>
                <p><span className="support-widget-status" /> Support assistant</p>
              </div>
            </div>
            <button
              className="support-widget-close"
              type="button"
              onClick={() => setIsOpen(false)}
              aria-label="Close support chat"
            >
              <X size={20} />
            </button>
          </header>

          <div
            className="support-widget-messages"
            ref={messagesRef}
            aria-live="polite"
            aria-busy={isSending}
          >
            <p className="support-widget-day">TODAY</p>
            {messages.map(
              (item) =>
                item.content && (
                  <div
                    className={`support-widget-message-row ${item.role}`}
                    key={item.id}
                  >
                    {item.role === 'assistant' && (
                      <span className="support-widget-message-avatar" aria-hidden="true">
                        <Headset size={15} />
                      </span>
                    )}
                    <p className="support-widget-message">{item.content}</p>
                  </div>
                ),
            )}
            {messages.length === 1 && !isSending && (
              <div
                className="support-widget-suggestions"
                role="group"
                aria-label="Common questions"
              >
                <p>Or choose a common question:</p>
                {suggestedQuestions.map((question) => (
                  <button
                    className="support-widget-suggestion"
                    key={question.label}
                    type="button"
                    onClick={() => void sendMessage(question.message)}
                  >
                    {question.label}
                  </button>
                ))}
              </div>
            )}
            {isTyping && (
              <div
                className="support-widget-message-row assistant"
                role="status"
                aria-label="Assistant is typing"
              >
                <span className="support-widget-message-avatar" aria-hidden="true">
                  <Headset size={15} />
                </span>
                <span className="support-widget-typing" aria-hidden="true">
                  <span />
                  <span />
                  <span />
                </span>
                <span className="support-widget-sr-only">Assistant is typing</span>
              </div>
            )}
          </div>

          <form className="support-widget-composer" onSubmit={handleSubmit}>
            <label className="support-widget-sr-only" htmlFor={inputId}>
              Type your message
            </label>
            <textarea
              id={inputId}
              ref={inputRef}
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              disabled={isSending}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault();
                  event.currentTarget.form?.requestSubmit();
                }
              }}
              placeholder="Type your message..."
              rows={1}
              maxLength={2000}
            />
            <button
              className="support-widget-send"
              type="submit"
              disabled={!message.trim() || isSending}
              aria-label="Send message"
            >
              <ArrowUp size={18} />
            </button>
            <p className="support-widget-composer-note">
              {isSending
                ? 'Getting an answer...'
                : 'We-Hive support · Enter to send, Shift+Enter for a new line'}
            </p>
          </form>
        </section>
      )}

      {showLauncher && (!isStandalone || !isOpen) && (
        <button
          className={`support-widget-launcher${isOpen ? ' is-open' : ''}`}
          type="button"
          onClick={() => setIsOpen((open) => !open)}
          aria-label={isOpen ? 'Close support chat' : 'Open support chat'}
          aria-expanded={isOpen}
        >
          {isOpen ? <ArrowDown size={23} /> : <MessageCircle size={24} />}
        </button>
      )}
    </main>
  );
}
