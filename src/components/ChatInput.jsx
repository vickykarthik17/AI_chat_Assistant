import { useRef, useEffect, useState } from 'react';
import { Send, Square } from 'lucide-react';

export default function ChatInput({ onSend, onStop, isStreaming, disabled }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  }, [text]);

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-white/10 bg-gray-900/80 px-4 py-4 backdrop-blur-xl sm:px-6">
      <div className="mx-auto flex max-w-3xl items-end gap-2">
        <div className="relative flex-1">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Send a message..."
            rows={1}
            disabled={disabled && !isStreaming}
            className="w-full resize-none rounded-2xl border border-white/10 bg-white/5 px-4 py-3 pr-12 text-sm text-gray-100 placeholder-gray-500 outline-none transition-all focus:border-sky-500/50 focus:bg-white/10 focus:ring-2 focus:ring-sky-500/20 disabled:opacity-50"
          />
        </div>
        {isStreaming ? (
          <button
            onClick={onStop}
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-red-500/20 text-red-400 ring-1 ring-red-500/30 transition-all hover:bg-red-500/30 hover:ring-red-500/50"
            title="Stop generating"
          >
            <Square className="h-4 w-4 fill-current" />
          </button>
        ) : (
          <button
            onClick={handleSend}
            disabled={disabled || !text.trim()}
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-500 to-cyan-500 text-white shadow-lg shadow-sky-500/30 transition-all hover:shadow-sky-500/50 disabled:cursor-not-allowed disabled:opacity-30 disabled:shadow-none"
            title="Send message"
          >
            <Send className="h-4 w-4" />
          </button>
        )}
      </div>
      <p className="mx-auto mt-2 max-w-3xl text-center text-xs text-gray-600">
        Press Enter to send, Shift+Enter for a new line
      </p>
    </div>
  );
}
