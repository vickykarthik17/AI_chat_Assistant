const API_BASE = '/api';
const API_TOKEN = import.meta.env.VITE_API_TOKEN || '';

function headers(contentType = false) {
  return {
    ...(contentType ? { 'Content-Type': 'application/json' } : {}),
    ...(API_TOKEN ? { Authorization: `Bearer ${API_TOKEN}` } : {}),
  };
}

async function handleResponse(res) {
  if (!res.ok) {
    const error = await res.text().catch(() => 'Request failed');
    throw new Error(error || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  async listSessions() {
    const res = await fetch(`${API_BASE}/sessions`, { headers: headers() });
    return handleResponse(res);
  },

  async createSession(title = 'New Chat') {
    const res = await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: headers(true),
      body: JSON.stringify({ title }),
    });
    return handleResponse(res);
  },

  async getSession(id) {
    const res = await fetch(`${API_BASE}/sessions/${id}`, { headers: headers() });
    return handleResponse(res);
  },

  async deleteSession(id) {
    const res = await fetch(`${API_BASE}/sessions/${id}`, { method: 'DELETE', headers: headers() });
    if (!res.ok) throw new Error('Failed to delete session');
  },

  async updateSession(id, title) {
    const res = await fetch(`${API_BASE}/sessions/${id}`, {
      method: 'PATCH',
      headers: headers(true),
      body: JSON.stringify({ title }),
    });
    return handleResponse(res);
  },

  async *streamChat(sessionId, message, signal) {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}/chat`, {
      method: 'POST',
      headers: headers(true),
      body: JSON.stringify({ message }),
      signal,
    });

    if (!res.ok) {
      const error = await res.text().catch(() => 'Chat request failed');
      throw new Error(error || `HTTP ${res.status}`);
    }

    const reader = res.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.startsWith('data:')) continue;
        const payload = line.slice(5).trim();
        if (!payload) continue;
        let obj;
        try {
          obj = JSON.parse(payload);
        } catch {
          continue;
        }
        if (obj.error) throw new Error(obj.error);
        if (obj.stop) return;
        if (obj.text) yield obj.text;
      }
    }
  },
};
