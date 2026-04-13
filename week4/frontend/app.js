async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  if (res.status === 204) return null;
  return res.json();
}

async function loadNotes(query = '') {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const endpoint = query.trim()
    ? `/notes/search/?q=${encodeURIComponent(query.trim())}`
    : '/notes/';
  const notes = await fetchJSON(endpoint);
  for (const n of notes) {
    const li = document.createElement('li');

    const text = document.createElement('span');
    text.textContent = `${n.title}: ${n.content}`;
    li.appendChild(text);

    const editBtn = document.createElement('button');
    editBtn.textContent = 'Edit';
    editBtn.onclick = async () => {
      const title = window.prompt('New title:', n.title);
      if (title === null) return;
      const content = window.prompt('New content:', n.content);
      if (content === null) return;
      await fetchJSON(`/notes/${n.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content }),
      });
      loadNotes(document.getElementById('note-search').value);
    };
    li.appendChild(editBtn);

    const delBtn = document.createElement('button');
    delBtn.textContent = 'Delete';
    delBtn.onclick = async () => {
      if (!window.confirm('Delete this note?')) return;
      await fetchJSON(`/notes/${n.id}`, { method: 'DELETE' });
      loadNotes(document.getElementById('note-search').value);
    };
    li.appendChild(delBtn);

    list.appendChild(li);
  }
}

async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const items = await fetchJSON('/action-items/');
  for (const a of items) {
    const li = document.createElement('li');
    li.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        loadActions();
      };
      li.appendChild(btn);
    }
    list.appendChild(li);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    loadNotes(document.getElementById('note-search').value);
  });

  document.getElementById('note-search-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    loadNotes(document.getElementById('note-search').value);
  });

  document.getElementById('note-clear-search').addEventListener('click', async () => {
    document.getElementById('note-search').value = '';
    loadNotes();
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    loadActions();
  });

  loadNotes();
  loadActions();
});
