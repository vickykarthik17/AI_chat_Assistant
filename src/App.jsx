import { useState, useEffect, useCallback, useRef } from 'react';
import { LoaderCircle, LogOut, Menu, UserRoundPlus } from 'lucide-react';
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
  const [authState, setAuthState] = useState('checking');
  const [authMode, setAuthMode] = useState('register');
  const [email, setEmail] = useState('');
  const [accountEmail, setAccountEmail] = useState('');
  const [password, setPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const abortRef = useRef(null);

  useEffect(() => {
    let active = true;
    api.authStatus()
      .then(({ authenticated, user }) => {
        if (active) {
          setAccountEmail(user?.email || '');
          setAuthState(authenticated ? 'authenticated' : 'signed-out');
        }
      })
      .catch(() => {
        if (active) setAuthState('unavailable');
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    const handleAuthRequired = () => {
      setSessions([]);
      setActiveSessionId(null);
      setMessages([]);
      setAccountEmail('');
      setAuthState('signed-out');
    };
    window.addEventListener('auth-required', handleAuthRequired);
    return () => window.removeEventListener('auth-required', handleAuthRequired);
  }, []);

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
    if (authState === 'authenticated') loadSessions();
  }, [authState, loadSessions]);

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

  async function handleAuthSubmit(event) {
    event.preventDefault();
    setAuthError('');
    setAuthState('signing-in');
    try {
      const result = authMode === 'register'
        ? await api.register(email, password)
        : await api.login(email, password);
      setAccountEmail(result.user.email);
      setEmail('');
      setPassword('');
      setAuthState('authenticated');
    } catch (error) {
      setAuthState('signed-out');
      setAuthError(error?.message || 'Authentication failed. Please try again.');
    }
  }

  async function handleLogout() {
    abortRef.current?.abort();
    try {
      await api.logout();
    } finally {
      setSessions([]);
      setActiveSessionId(null);
      setMessages([]);
      setAccountEmail('');
      setAuthState('signed-out');
    }
  }

  const activeSession = sessions.find((s) => s.id === activeSessionId);
  const sessionTitle = activeSession?.title || 'New Chat';

  if (authState !== 'authenticated') {
    const checking = authState === 'checking';
    const signingIn = authState === 'signing-in';
    const registering = authMode === 'register';

    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-950 px-4 text-gray-100">
        <section className="w-full max-w-sm rounded-xl border border-white/10 bg-gray-900 p-7 shadow-2xl shadow-black/30">
          <div className="mb-6 flex h-11 w-11 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-gray-200">
            {checking ? <LoaderCircle className="h-5 w-5 animate-spin" /> : <UserRoundPlus className="h-5 w-5" />}
          </div>
          <p className="mb-2 text-xs font-medium uppercase tracking-widest text-gray-500">AI Chat</p>
          <h1 className="text-xl font-semibold text-white">
            {registering ? 'Create your account' : 'Welcome back'}
          </h1>
          <p className="mt-2 text-sm text-gray-400">
            Your conversations are private to your account.
          </p>
          <form className="mt-6 space-y-4" onSubmit={handleAuthSubmit}>
            <div className="space-y-2">
              <label htmlFor="account-email" className="text-sm text-gray-300">Email</label>
              <input
                id="account-email"
                type="email"
                autoComplete="email"
                required
                maxLength={254}
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                disabled={checking || signingIn}
                className="w-full rounded-lg border border-white/10 bg-gray-950 px-3 py-2.5 text-sm text-white outline-none transition focus:border-gray-500 focus:ring-2 focus:ring-white/10 disabled:opacity-60"
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="account-password" className="text-sm text-gray-300">Password</label>
              <input
                id="account-password"
                type="password"
                autoComplete={registering ? 'new-password' : 'current-password'}
                required
                minLength={12}
                maxLength={1024}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                disabled={checking || signingIn}
                className="w-full rounded-lg border border-white/10 bg-gray-950 px-3 py-2.5 text-sm text-white outline-none transition focus:border-gray-500 focus:ring-2 focus:ring-white/10 disabled:opacity-60"
              />
              {registering && (
                <p className="text-xs text-gray-500">Use at least 12 characters.</p>
              )}
            </div>
            {authError && <p role="alert" className="text-sm text-red-300">{authError}</p>}
            {authState === 'unavailable' && !authError && (
              <p role="status" className="text-sm text-amber-200">Unable to reach the sign-in service.</p>
            )}
            <button
              type="submit"
              disabled={checking || signingIn}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-white px-4 py-2.5 text-sm font-semibold text-gray-900 transition hover:bg-gray-200 disabled:cursor-wait disabled:opacity-60"
            >
              {signingIn && <LoaderCircle className="h-4 w-4 animate-spin" />}
              {signingIn ? 'Please wait...' : registering ? 'Create account' : 'Sign in'}
            </button>
          </form>
          <p className="mt-5 text-center text-sm text-gray-400">
            {registering ? 'Already have an account?' : 'New here?'}{' '}
            <button
              type="button"
              onClick={() => {
                setAuthMode(registering ? 'login' : 'register');
                setAuthError('');
              }}
              className="font-medium text-white hover:underline"
            >
              {registering ? 'Sign in' : 'Create an account'}
            </button>
          </p>
        </section>
      </main>
    );
  }

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
          <span className="ml-auto hidden max-w-48 truncate text-xs text-gray-500 sm:block">
            {accountEmail}
          </span>
          <button
            onClick={handleLogout}
            aria-label="Sign out"
            title="Sign out"
            className="rounded-lg p-1.5 text-gray-400 transition-colors hover:bg-white/10 hover:text-white"
          >
            <LogOut className="h-4 w-4" />
          </button>
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
