import { User, Sparkles } from 'lucide-react';
import MarkdownRenderer from './MarkdownRenderer';

export default function MessageBubble({ message, isStreaming = false }) {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end gap-3 px-4 py-3 sm:px-6">
        <div className="flex max-w-[75%] flex-col items-end gap-1">
          <div className="rounded-2xl rounded-tr-sm bg-sky-600 px-4 py-2.5 text-sm leading-relaxed text-white shadow-lg shadow-sky-600/20">
            <MarkdownRenderer content={message.content} />
          </div>
        </div>
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-sky-600/20 ring-1 ring-sky-500/30">
          <User className="h-4 w-4 text-sky-400" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start gap-3 px-4 py-3 sm:px-6">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-sky-500 to-cyan-500 shadow-lg shadow-cyan-500/20">
        <Sparkles className="h-4 w-4 text-white" />
      </div>
      <div className="flex max-w-[75%] flex-col gap-1">
        <div className="rounded-2xl rounded-tl-sm bg-white/5 px-4 py-2.5 text-sm leading-relaxed text-gray-100 ring-1 ring-white/10">
          {message.content ? (
            <MarkdownRenderer content={message.content} />
          ) : isStreaming ? (
            <span className="inline-flex items-center gap-1">
              <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:-0.3s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:-0.15s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400" />
            </span>
          ) : null}
          {isStreaming && message.content && (
            <span className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-sky-400 align-middle" />
          )}
        </div>
      </div>
    </div>
  );
}
