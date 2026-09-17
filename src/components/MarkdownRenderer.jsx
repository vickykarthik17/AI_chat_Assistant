import { memo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

function MarkdownRenderer({ content }) {
  return (
    <div className="prose prose-sm prose-invert max-w-none prose-p:my-2 prose-p:leading-relaxed prose-pre:my-3 prose-pre:bg-black/40 prose-pre:border prose-pre:border-white/10 prose-code:before:hidden prose-code:after:hidden prose-code:bg-white/10 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-[0.85em] prose-code:font-normal prose-headings:scroll-mt-20 prose-a:text-sky-400 prose-strong:text-white prose-ol:my-2 prose-ul:my-2 prose-li:my-0.5 prose-blockquote:border-l-sky-400/50 prose-blockquote:text-gray-400">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  );
}

export default memo(MarkdownRenderer);
