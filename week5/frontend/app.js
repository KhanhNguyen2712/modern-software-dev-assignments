async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  const body = await res.json();
  if (body.ok === false) throw new Error(body.error?.message || 'Request failed');
  return body.data;
}

let notesState = [];
let notesStatusMessage = '';

function renderNotes() {
  const list = document.getElementById('notes');
  const status = document.getElementById('notes-status');
  list.innerHTML = '';
  status.textContent = notesStatusMessage;

  for (const note of notesState) {
    const li = document.createElement('li');
    li.textContent = `${note.title}: ${note.content}`;

    const editBtn = document.createElement('button');
    editBtn.textContent = 'Edit';
    editBtn.onclick = async () => {
      const nextTitle = window.prompt('Edit title', note.title);
      if (nextTitle === null) return;
      const nextContent = window.prompt('Edit content', note.content);
      if (nextContent === null) return;

      const previousState = [...notesState];
      notesState = notesState.map((current) =>
        current.id === note.id ? { ...current, title: nextTitle, content: nextContent } : current,
      );
      renderNotes();

      try {
        const updated = await fetchJSON(`/notes/${note.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: nextTitle, content: nextContent }),
        });
        notesState = notesState.map((current) => (current.id === note.id ? updated : current));
        renderNotes();
      } catch (error) {
        notesState = previousState;
        notesStatusMessage = `Edit failed: ${error.message}`;
        renderNotes();
      }
    };

    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'Delete';
    deleteBtn.onclick = async () => {
      const previousState = [...notesState];
      notesState = notesState.filter((current) => current.id !== note.id);
      renderNotes();

      try {
        await fetchJSON(`/notes/${note.id}`, { method: 'DELETE' });
      } catch (error) {
        notesState = previousState;
        notesStatusMessage = `Delete failed: ${error.message}`;
        renderNotes();
      }
    };

    li.appendChild(editBtn);
    li.appendChild(deleteBtn);
    list.appendChild(li);
  }
}

async function loadNotes() {
  const notesPage = await fetchJSON('/notes/');
  notesState = notesPage.items;
  notesStatusMessage = '';
  renderNotes();
}

async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const itemsPage = await fetchJSON('/action-items/');
  for (const a of itemsPage.items) {
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
