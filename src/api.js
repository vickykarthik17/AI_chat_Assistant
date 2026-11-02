const API_BASE = '/api';

function headers(contentType = false) {
  return {
    ...(contentType ? { 'Content-Type': 'application/json' } : {}),
  };
}

async function fetchApi(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: 'same-origin',
    ...options,
  });
  if (res.status === 401 && path !== '/auth/login' && path !== '/auth/status') {
    window.dispatchEvent(new Event('auth-required'));
  }
  return res;
}

async function handleResponse(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const detail = body?.detail;
    const message = Array.isArray(detail)
      ? detail.map((issue) => issue.msg).join(' ')
      : typeof detail === 'string'
        ? detail
        : `Request failed (HTTP ${res.status})`;
    throw new Error(message);
  }
  return res.json();
}

export const api = {
  async authStatus() {
    const res = await fetchApi('/auth/status');
    return handleResponse(res);
  },

  async register(email, password) {
    const res = await fetchApi('/auth/register', {
      method: 'POST',
      headers: headers(true),
      body: JSON.stringify({ email, password }),
    });
    return handleResponse(res);
  },

  async login(email, password) {
    const res = await fetchApi('/auth/login', {
      method: 'POST',
      headers: headers(true),
      body: JSON.stringify({ email, password }),
    });
    return handleResponse(res);
  },

  async logout() {
    const res = await fetchApi('/auth/logout', { method: 'POST' });
    return handleResponse(res);
  },

  async listSessions() {
    const res = await fetchApi('/sessions', { headers: headers() });
    return handleResponse(res);
  },

  async createSession(title = 'New Chat') {
    const res = await fetchApi('/sessions', {
      method: 'POST',
      headers: headers(true),
      body: JSON.stringify({ title }),
    });
    return handleResponse(res);
  },

  async getSession(id) {
    const res = await fetchApi(`/sessions/${id}`, { headers: headers() });
    return handleResponse(res);
  },

  async deleteSession(id) {
    const res = await fetchApi(`/sessions/${id}`, { method: 'DELETE', headers: headers() });
    if (!res.ok) throw new Error('Failed to delete session');
  },

  async updateSession(id, title) {
    const res = await fetchApi(`/sessions/${id}`, {
      method: 'PATCH',
      headers: headers(true),
      body: JSON.stringify({ title }),
    });
    return handleResponse(res);
  },

  async *streamChat(sessionId, message, signal) {
    const res = await fetchApi(`/sessions/${sessionId}/chat`, {
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
