import { useState } from 'react';
import { Plus, MessageSquare, Trash2, X, Pencil, Check, Sparkles } from 'lucide-react';

export default function Sidebar({
  sessions,
  activeSessionId,
  onSelect,
  onCreate,
  onDelete,
  onRename,
  isOpen,
  onClose,
}) {
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');

  const startEdit = (s) => {
    setEditingId(s.id);
    setEditText(s.title);
  };

  const commitEdit = () => {
    if (editingId && editText.trim()) {
      onRename(editingId, editText.trim());
    }
    setEditingId(null);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    commitEdit();
  };

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed left-0 top-0 z-40 flex h-full w-72 flex-col border-r border-white/10 bg-gray-950/95 backdrop-blur-xl transition-transform duration-300 lg:relative lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between px-4 py-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-sky-500 to-cyan-500 shadow-lg shadow-sky-500/30">
              <Sparkles className="h-4 w-4 text-white" />
            </div>
            <span className="text-sm font-semibold text-gray-200">AI Chat</span>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-gray-400 transition-colors hover:bg-white/10 hover:text-white lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="px-3 pb-2">
          <button
            onClick={onCreate}
            className="flex w-full items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-sm font-medium text-gray-200 transition-all hover:bg-white/10 hover:ring-1 hover:ring-sky-500/30"
          >
            <Plus className="h-4 w-4 text-sky-400" />
            New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-2 py-2">
          {sessions.length === 0 ? (
            <p className="px-3 py-8 text-center text-xs text-gray-600">No conversations yet</p>
          ) : (
            <div className="space-y-0.5">
              {sessions.map((s) => (
                <div
                  key={s.id}
                  className={`group flex items-center gap-2 rounded-lg px-2.5 py-2 transition-colors ${
                    activeSessionId === s.id
                      ? 'bg-white/10 ring-1 ring-sky-500/20'
                      : 'hover:bg-white/5'
                  }`}
                >
                  <MessageSquare
                    className={`h-4 w-4 shrink-0 ${
                      activeSessionId === s.id ? 'text-sky-400' : 'text-gray-500'
                    }`}
                  />
                  {editingId === s.id ? (
                    <form onSubmit={handleSubmit} className="flex flex-1 items-center gap-1">
                      <input
                        autoFocus
                        value={editText}
                        onChange={(e) => setEditText(e.target.value)}
                        onBlur={commitEdit}
                        className="flex-1 rounded bg-black/30 px-2 py-1 text-sm text-gray-200 outline-none ring-1 ring-sky-500/40"
                      />
                      <button type="submit" className="text-sky-400 hover:text-sky-300">
                        <Check className="h-4 w-4" />
                      </button>
                    </form>
                  ) : (
                    <>
                      <button
                        onClick={() => onSelect(s.id)}
                        className="flex-1 truncate text-left text-sm text-gray-300"
                      >
                        {s.title}
                      </button>
                      <button
                        onClick={() => startEdit(s)}
                        className="shrink-0 text-gray-600 opacity-0 transition-all hover:text-gray-300 group-hover:opacity-100"
                      >
                        <Pencil className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => onDelete(s.id)}
                        className="shrink-0 text-gray-600 opacity-0 transition-all hover:text-red-400 group-hover:opacity-100"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="border-t border-white/10 px-4 py-3">
          <p className="text-xs text-gray-600">Powered by Claude 3.5 Sonnet</p>
        </div>
      </aside>
    </>
  );
}
