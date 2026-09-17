import { useEffect, useRef } from 'react';
import { Sparkles, AlertCircle } from 'lucide-react';
import MessageBubble from './MessageBubble';

export default function ChatArea({ messages, isStreaming, error, sessionTitle }) {
  const scrollRef = useRef(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, isStreaming]);

  const isEmpty = messages.length === 0 && !error;

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2 border-b border-white/10 px-4 py-3 sm:px-6">
        <h2 className="truncate text-sm font-medium text-gray-300">{sessionTitle}</h2>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto">
        {isEmpty ? (
          <div className="flex h-full flex-col items-center justify-center gap-6 px-4 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-3xl bg-gradient-to-br from-sky-500 to-cyan-500 shadow-2xl shadow-sky-500/30">
              <Sparkles className="h-8 w-8 text-white" />
            </div>
            <div className="space-y-1">
              <h3 className="text-lg font-semibold text-gray-200">How can I help you today?</h3>
              <p className="text-sm text-gray-500">Ask anything — I can help with writing, code, analysis, and more.</p>
            </div>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {[
                'Explain quantum computing in simple terms',
                'Write a haiku about the ocean',
                'Help me debug a Python error',
                'Give me ideas for a weekend project',
              ].map((suggestion) => (
                <div
                  key={suggestion}
                  className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-left text-sm text-gray-400 transition-colors hover:bg-white/10"
                >
                  {suggestion}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="py-4">
            {messages.map((msg, i) => {
              const isLast = i === messages.length - 1;
              return (
                <MessageBubble
                  key={i}
                  message={msg}
                  isStreaming={isLast && isStreaming && msg.role === 'assistant'}
                />
              );
            })}
            {error && (
              <div className="mx-4 my-2 flex items-center gap-2 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300 sm:mx-6">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>
    </div>
  );
}
