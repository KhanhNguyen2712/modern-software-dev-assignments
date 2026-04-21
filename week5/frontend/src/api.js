const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

function buildUrl(path, params) {
  const url = new URL(`${API_BASE_URL}${path}`, window.location.origin);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value === null || value === undefined || value === '') {
        return;
      }
      url.searchParams.set(key, String(value));
    });
  }
  return `${url.pathname}${url.search}`;
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const body = await response.json();
  if (!response.ok || body.ok === false) {
    throw new Error(body.error?.message || 'Request failed');
  }
  return body.data;
}

export function listNotes(params) {
  return request(buildUrl('/notes/search', params));
}

export function createNote(payload) {
  return request('/notes/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function updateNote(noteId, payload) {
  return request(`/notes/${noteId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function deleteNote(noteId) {
  return request(`/notes/${noteId}`, { method: 'DELETE' });
}

export function extractNote(noteId, apply = false) {
  return request(buildUrl(`/notes/${noteId}/extract`, apply ? { apply: true } : undefined), {
    method: 'POST',
  });
}

export function listTags() {
  return request('/tags/');
}

export function createTag(payload) {
  return request('/tags/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function listActionItems(params) {
  return request(buildUrl('/action-items/', params));
}

export function createActionItem(payload) {
  return request('/action-items/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function completeActionItem(itemId) {
  return request(`/action-items/${itemId}/complete`, { method: 'PUT' });
}

export function bulkCompleteActionItems(ids) {
  return request('/action-items/bulk-complete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ids }),
  });
}
