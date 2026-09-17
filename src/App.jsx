import { useState, useEffect, useCallback, useRef } from 'react';
import { Menu } from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import ChatArea from '@/components/ChatArea';
import ChatInput from '@/components/ChatInput';
import { api } from '@/api';

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loadingSession, setLoadingSession] = useState(false);
  const abortRef = useRef(null);

  const loadSessions = useCallback(async () => {
    try {
      const list = await api.listSessions();
      list.sort((a, b) => b.updated_at.localeCompare(a.updated_at));
      setSessions(list);
    } catch {
      // backend may not be running yet
    }
  }, []);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  const handleCreate = useCallback(async () => {
    try {
      const s = await api.createSession('New Chat');
      setSessions((prev) => [s, ...prev]);
      setActiveSessionId(s.id);
      setMessages([]);
      setError(null);
      setSidebarOpen(false);
    } catch {
      setError('Failed to create a new conversation. Is the backend running?');
    }
  }, []);

  const handleSelect = useCallback(async (id) => {
    if (isStreaming) return;
    setActiveSessionId(id);
    setMessages([]);
    setError(null);
    setLoadingSession(true);
    setSidebarOpen(false);
    try {
      const s = await api.getSession(id);
      setMessages(s.messages || []);
    } catch {
      setError('Failed to load conversation.');
    } finally {
      setLoadingSession(false);
    }
  }, [isStreaming]);

  const handleDelete = useCallback(async (id) => {
    try {
      await api.deleteSession(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
      if (activeSessionId === id) {
        setActiveSessionId(null);
        setMessages([]);
      }
    } catch {
      setError('Failed to delete conversation.');
    }
  }, [activeSessionId]);

  const handleRename = useCallback(async (id, title) => {
    try {
      await api.updateSession(id, title);
      setSessions((prev) =>
        prev.map((s) => (s.id === id ? { ...s, title } : s))
      );
    } catch {
      setError('Failed to rename conversation.');
    }
  }, []);

  const handleSend = useCallback(async (text) => {
    let sessionId = activeSessionId;

    if (!sessionId) {
      try {
        const s = await api.createSession(text.slice(0, 40) || 'New Chat');
        sessionId = s.id;
        setSessions((prev) => [s, ...prev]);
        setActiveSessionId(s.id);
      } catch {
        setError('Failed to create a conversation. Is the backend running?');
        return;
      }
    }

    const userMessage = { role: 'user', content: text };
    const assistantMessage = { role: 'assistant', content: '' };
    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setError(null);
    setIsStreaming(true);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      let firstChunk = true;
      for await (const chunk of api.streamChat(sessionId, text, controller.signal)) {
        if (firstChunk) {
          firstChunk = false;
          if (activeSessionId === null) {
            setSessions((prev) => {
              if (prev.length === 0 || prev[0].id !== sessionId) return prev;
              return [
                { ...prev[0], title: text.slice(0, 40) || 'New Chat' },
                ...prev.slice(1),
              ];
            });
          }
        }
        setMessages((prev) => {
          const next = [...prev];
          const last = next[next.length - 1];
          if (last && last.role === 'assistant') {
            next[next.length - 1] = { ...last, content: last.content + chunk };
          }
          return next;
        });
      }
    } catch (err) {
      if (err?.name !== 'AbortError') {
        setError(err?.message || 'Failed to get a response.');
      }
    } finally {
      setIsStreaming(false);
      abortRef.current = null;
      loadSessions();
    }
  }, [activeSessionId, loadSessions]);

  const handleStop = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  const activeSession = sessions.find((s) => s.id === activeSessionId);
  const sessionTitle = activeSession?.title || 'New Chat';

  return (
    <div className="flex h-screen overflow-hidden bg-gray-900 text-gray-100">
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelect={handleSelect}
        onCreate={handleCreate}
        onDelete={handleDelete}
        onRename={handleRename}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-3 border-b border-white/10 bg-gray-900/80 px-4 py-3 backdrop-blur-xl sm:px-6">
          <button
            onClick={() => setSidebarOpen(true)}
            className="rounded-lg p-1.5 text-gray-400 transition-colors hover:bg-white/10 hover:text-white lg:hidden"
          >
            <Menu className="h-5 w-5" />
          </button>
          <h1 className="truncate text-sm font-medium text-gray-300">{sessionTitle}</h1>
        </header>

        <main className="flex min-h-0 flex-1 flex-col">
          <div className="min-h-0 flex-1">
            <ChatArea
              messages={messages}
              isStreaming={isStreaming}
              error={error}
              sessionTitle={sessionTitle}
            />
          </div>
          <ChatInput
            onSend={handleSend}
            onStop={handleStop}
            isStreaming={isStreaming}
            disabled={loadingSession}
          />
        </main>
      </div>
    </div>
  );
}
