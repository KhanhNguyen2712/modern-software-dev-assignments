const state = {
  notes: [],
  notesTotal: 0,
  notesPage: 1,
  notesPageSize: 5,
  notesQuery: '',
  notesSort: 'created_desc',
  editingNoteId: null,
  actionItems: [],
  actionFilter: 'all',
  selectedActionIds: new Set(),
};

const refs = {};

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);
  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get('content-type') || '';
  const payload = contentType.includes('application/json')
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail = typeof payload === 'object' && payload !== null ? payload.detail : payload;
    throw new Error(detail || 'Request failed');
  }

  return payload;
}

function initRefs() {
  refs.status = document.getElementById('status-message');
  refs.noteForm = document.getElementById('note-form');
  refs.noteTitle = document.getElementById('note-title');
  refs.noteContent = document.getElementById('note-content');
  refs.noteSubmit = document.getElementById('note-submit');
  refs.noteCancel = document.getElementById('note-cancel');
  refs.noteSearchForm = document.getElementById('note-search-form');
  refs.noteSearch = document.getElementById('note-search');
  refs.noteSort = document.getElementById('note-sort');
  refs.notesList = document.getElementById('notes');
  refs.notesSummary = document.getElementById('notes-summary');
  refs.notesPageLabel = document.getElementById('notes-page-label');
  refs.notesPrev = document.getElementById('notes-prev');
  refs.notesNext = document.getElementById('notes-next');
  refs.actionForm = document.getElementById('action-form');
  refs.actionDesc = document.getElementById('action-desc');
  refs.actionFilters = document.getElementById('action-filters');
  refs.actionsList = document.getElementById('actions');
  refs.bulkComplete = document.getElementById('bulk-complete');
}

function setStatus(message, tone = 'info') {
  if (!message) {
    refs.status.hidden = true;
    refs.status.textContent = '';
    refs.status.removeAttribute('data-tone');
    return;
  }

  refs.status.hidden = false;
  refs.status.textContent = message;
  refs.status.dataset.tone = tone;
}

function escapeHTML(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
}

function formatDate(isoValue) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(isoValue));
}

function totalNotePages() {
  return Math.max(1, Math.ceil(state.notesTotal / state.notesPageSize));
}

function syncNoteControls() {
  refs.notesSummary.textContent = `${state.notesTotal} result${state.notesTotal === 1 ? '' : 's'}`;
  refs.notesPageLabel.textContent = `Page ${state.notesPage} of ${totalNotePages()}`;
  refs.notesPrev.disabled = state.notesPage <= 1;
  refs.notesNext.disabled = state.notesPage >= totalNotePages();
}

function resetNoteForm() {
  state.editingNoteId = null;
  refs.noteForm.reset();
  refs.noteSearch.value = state.notesQuery;
  refs.noteSort.value = state.notesSort;
  refs.noteSubmit.textContent = 'Add note';
  refs.noteCancel.hidden = true;
}

function startEditingNote(note) {
  state.editingNoteId = note.id;
  refs.noteTitle.value = note.title;
  refs.noteContent.value = note.content;
  refs.noteSubmit.textContent = 'Save note';
  refs.noteCancel.hidden = false;
  refs.noteTitle.focus();
}

function setNoteInState(note) {
  const index = state.notes.findIndex((item) => item.id === note.id);
  if (index >= 0) {
    state.notes[index] = note;
    return;
  }
  state.notes.unshift(note);
}

function removeNoteFromState(noteId) {
  const index = state.notes.findIndex((item) => item.id === noteId);
  if (index < 0) {
    return null;
  }
  const [removed] = state.notes.splice(index, 1);
  return { note: removed, index };
}

function renderEmptyState(list, message) {
  list.innerHTML = `<li class="empty-state">${escapeHTML(message)}</li>`;
}

function renderNotes() {
  syncNoteControls();
  if (!state.notes.length) {
    renderEmptyState(refs.notesList, 'No notes match the current search.');
    return;
  }

  refs.notesList.innerHTML = '';
  for (const note of state.notes) {
    const li = document.createElement('li');
    li.className = `card-item${note.pending ? ' pending' : ''}`;
    li.innerHTML = `
      <div class="note-meta">
        <strong>${escapeHTML(note.title)}</strong>
        <span>${formatDate(note.updated_at)}</span>
      </div>
      <p class="note-copy">${escapeHTML(note.content)}</p>
      <div class="note-meta">
        <span>Created ${formatDate(note.created_at)}</span>
        <div class="note-actions">
          <button type="button" class="ghost" data-action="edit">Edit</button>
          <button type="button" class="ghost" data-action="delete">Delete</button>
        </div>
      </div>
    `;

    li.querySelector('[data-action="edit"]').addEventListener('click', () => startEditingNote(note));
    li.querySelector('[data-action="delete"]').addEventListener('click', () => deleteNote(note.id));
    refs.notesList.appendChild(li);
  }
}

async function loadNotes() {
  const params = new URLSearchParams({
    q: state.notesQuery,
    page: String(state.notesPage),
    page_size: String(state.notesPageSize),
    sort: state.notesSort,
  });
  const data = await fetchJSON(`/notes/search?${params.toString()}`);

  const maxPage = Math.max(1, Math.ceil(data.total / state.notesPageSize));
  if (data.total > 0 && state.notesPage > maxPage) {
    state.notesPage = maxPage;
    return loadNotes();
  }

  state.notes = data.items;
  state.notesTotal = data.total;
  renderNotes();
}

async function handleNoteSubmit(event) {
  event.preventDefault();

  const title = refs.noteTitle.value.trim();
  const content = refs.noteContent.value.trim();
  if (!title || !content) {
    setStatus('Title and content are required.', 'error');
    return;
  }

  setStatus('');

  if (state.editingNoteId !== null) {
    const previous = state.notes.find((note) => note.id === state.editingNoteId);
    if (!previous) {
      return;
    }

    const optimisticNote = {
      ...previous,
      title,
      content,
      updated_at: new Date().toISOString(),
    };

    setNoteInState(optimisticNote);
    renderNotes();
    resetNoteForm();

    try {
      const savedNote = await fetchJSON(`/notes/${previous.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content }),
      });
      setNoteInState(savedNote);
      renderNotes();
      setStatus('Note updated.', 'success');
    } catch (error) {
      setNoteInState(previous);
      renderNotes();
      startEditingNote(previous);
      setStatus(error.message, 'error');
    }
    return;
  }

  const tempId = `temp-${Date.now()}`;
  const tempNote = {
    id: tempId,
    title,
    content,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    pending: true,
  };
  const matchesFilter =
    !state.notesQuery ||
    title.toLowerCase().includes(state.notesQuery.toLowerCase()) ||
    content.toLowerCase().includes(state.notesQuery.toLowerCase());
  const showOptimistically = matchesFilter && state.notesPage === 1;

  if (showOptimistically) {
    state.notesTotal += 1;
    state.notes = [tempNote, ...state.notes].slice(0, state.notesPageSize);
    renderNotes();
  }

  refs.noteForm.reset();

  try {
    await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    state.notesPage = 1;
    await loadNotes();
    setStatus('Note created.', 'success');
  } catch (error) {
    if (showOptimistically) {
      removeNoteFromState(tempId);
      state.notesTotal = Math.max(0, state.notesTotal - 1);
      renderNotes();
    }
    refs.noteTitle.value = title;
    refs.noteContent.value = content;
    setStatus(error.message, 'error');
  }
}

async function deleteNote(noteId) {
  const removed = removeNoteFromState(noteId);
  if (!removed) {
    return;
  }

  const previousTotal = state.notesTotal;
  state.notesTotal = Math.max(0, state.notesTotal - 1);
  if (!state.notes.length && state.notesPage > 1) {
    state.notesPage -= 1;
  }
  renderNotes();

  if (state.editingNoteId === noteId) {
    resetNoteForm();
  }

  try {
    await fetchJSON(`/notes/${noteId}`, { method: 'DELETE' });
    await loadNotes();
    setStatus('Note deleted.', 'success');
  } catch (error) {
    state.notes.splice(removed.index, 0, removed.note);
    state.notesTotal = previousTotal;
    renderNotes();
    setStatus(error.message, 'error');
  }
}

function syncActionSelection() {
  const selectableIds = new Set(
    state.actionItems.filter((item) => !item.completed).map((item) => item.id),
  );
  state.selectedActionIds = new Set(
    [...state.selectedActionIds].filter((itemId) => selectableIds.has(itemId)),
  );
  refs.bulkComplete.disabled = state.selectedActionIds.size === 0;
}

function renderActions() {
  syncActionSelection();

  for (const button of refs.actionFilters.querySelectorAll('button')) {
    button.classList.toggle('active', button.dataset.filter === state.actionFilter);
  }

  if (!state.actionItems.length) {
    renderEmptyState(refs.actionsList, 'No action items in this filter.');
    return;
  }

  refs.actionsList.innerHTML = '';
  for (const item of state.actionItems) {
    const li = document.createElement('li');
    li.className = 'card-item';

    const statusMarkup = item.completed ? '<span class="badge">Completed</span>' : '';
    li.innerHTML = `
      <div class="action-row">
        <div class="action-main">
          <label>
            <input type="checkbox" data-role="select" ${item.completed ? 'disabled' : ''} ${
              state.selectedActionIds.has(item.id) ? 'checked' : ''
            } />
            <span>${escapeHTML(item.description)}</span>
          </label>
          ${statusMarkup}
        </div>
        <div class="note-actions">
          ${item.completed ? '' : '<button type="button" data-role="complete">Complete</button>'}
        </div>
      </div>
    `;

    li.querySelector('[data-role="select"]').addEventListener('change', (event) => {
      if (event.target.checked) {
        state.selectedActionIds.add(item.id);
      } else {
        state.selectedActionIds.delete(item.id);
      }
      refs.bulkComplete.disabled = state.selectedActionIds.size === 0;
    });

    const completeButton = li.querySelector('[data-role="complete"]');
    if (completeButton) {
      completeButton.addEventListener('click', () => completeActionItem(item.id));
    }

    refs.actionsList.appendChild(li);
  }
}

async function loadActions() {
  const params = new URLSearchParams();
  if (state.actionFilter === 'open') {
    params.set('completed', 'false');
  } else if (state.actionFilter === 'done') {
    params.set('completed', 'true');
  }

  const queryString = params.toString();
  const url = queryString ? `/action-items/?${queryString}` : '/action-items/';
  state.actionItems = await fetchJSON(url);
  renderActions();
}

async function handleActionSubmit(event) {
  event.preventDefault();
  const description = refs.actionDesc.value.trim();
  if (!description) {
    setStatus('Description is required.', 'error');
    return;
  }

  try {
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    refs.actionForm.reset();
    await loadActions();
    setStatus('Action item created.', 'success');
  } catch (error) {
    setStatus(error.message, 'error');
  }
}

async function completeActionItem(itemId) {
  const previous = state.actionItems.map((item) => ({ ...item }));
  state.actionItems = state.actionItems.map((item) =>
    item.id === itemId ? { ...item, completed: true } : item,
  );
  state.selectedActionIds.delete(itemId);
  renderActions();

  try {
    await fetchJSON(`/action-items/${itemId}/complete`, { method: 'PUT' });
    await loadActions();
    setStatus('Action item completed.', 'success');
  } catch (error) {
    state.actionItems = previous;
    renderActions();
    setStatus(error.message, 'error');
  }
}

async function bulkCompleteSelected() {
  const selectedIds = [...state.selectedActionIds];
  if (!selectedIds.length) {
    return;
  }

  const previous = state.actionItems.map((item) => ({ ...item }));
  state.actionItems = state.actionItems.map((item) =>
    selectedIds.includes(item.id) ? { ...item, completed: true } : item,
  );
  state.selectedActionIds.clear();
  renderActions();

  try {
    await fetchJSON('/action-items/bulk-complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids: selectedIds }),
    });
    await loadActions();
    setStatus(`Completed ${selectedIds.length} action item(s).`, 'success');
  } catch (error) {
    state.actionItems = previous;
    renderActions();
    setStatus(error.message, 'error');
  }
}

function wireEvents() {
  refs.noteForm.addEventListener('submit', handleNoteSubmit);
  refs.noteCancel.addEventListener('click', resetNoteForm);
  refs.noteSearchForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    state.notesQuery = refs.noteSearch.value.trim();
    state.notesPage = 1;
    try {
      await loadNotes();
      setStatus('');
    } catch (error) {
      setStatus(error.message, 'error');
    }
  });
  refs.noteSort.addEventListener('change', async (event) => {
    state.notesSort = event.target.value;
    state.notesPage = 1;
    try {
      await loadNotes();
      setStatus('');
    } catch (error) {
      setStatus(error.message, 'error');
    }
  });
  refs.notesPrev.addEventListener('click', async () => {
    if (state.notesPage <= 1) {
      return;
    }
    state.notesPage -= 1;
    try {
      await loadNotes();
    } catch (error) {
      state.notesPage += 1;
      setStatus(error.message, 'error');
    }
  });
  refs.notesNext.addEventListener('click', async () => {
    if (state.notesPage >= totalNotePages()) {
      return;
    }
    state.notesPage += 1;
    try {
      await loadNotes();
    } catch (error) {
      state.notesPage -= 1;
      setStatus(error.message, 'error');
    }
  });

  refs.actionForm.addEventListener('submit', handleActionSubmit);
  refs.bulkComplete.addEventListener('click', bulkCompleteSelected);
  refs.actionFilters.addEventListener('click', async (event) => {
    const target = event.target.closest('button[data-filter]');
    if (!target || target.dataset.filter === state.actionFilter) {
      return;
    }
    state.actionFilter = target.dataset.filter;
    try {
      await loadActions();
      setStatus('');
    } catch (error) {
      setStatus(error.message, 'error');
    }
  });
}

window.addEventListener('DOMContentLoaded', async () => {
  initRefs();
  wireEvents();
  resetNoteForm();

  try {
    await Promise.all([loadNotes(), loadActions()]);
  } catch (error) {
    setStatus(error.message, 'error');
  }
});
