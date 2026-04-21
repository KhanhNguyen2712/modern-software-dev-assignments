import { useEffect, useState } from 'react';

import {
  bulkCompleteActionItems,
  completeActionItem,
  createActionItem,
  createNote,
  createTag,
  deleteNote,
  extractNote,
  listActionItems,
  listNotes,
  listTags,
  updateNote,
} from './api';
import { ActionItemsPanel } from './components/ActionItemsPanel';
import { NotesPanel } from './components/NotesPanel';

function toPageState(data, fallbackPageSize) {
  return {
    items: data.items,
    total: data.total,
    page: data.page,
    pageSize: data.page_size ?? fallbackPageSize,
  };
}

export default function App() {
  const [noteDraft, setNoteDraft] = useState({ title: '', content: '' });
  const [tagDraft, setTagDraft] = useState('');
  const [notesPage, setNotesPage] = useState({ items: [], total: 0, page: 1, pageSize: 5 });
  const [searchState, setSearchState] = useState({ query: '', sort: 'created_desc', tagId: null });
  const [availableTags, setAvailableTags] = useState([]);
  const [statusMessage, setStatusMessage] = useState('');
  const [actionDraft, setActionDraft] = useState('');
  const [actionsPage, setActionsPage] = useState({ items: [], total: 0, page: 1, pageSize: 10 });
  const [actionFilter, setActionFilter] = useState(null);
  const [selectedIds, setSelectedIds] = useState(new Set());

  async function refreshNotes(overrides = {}) {
    const nextState = {
      query: overrides.query ?? searchState.query,
      sort: overrides.sort ?? searchState.sort,
      tagId: overrides.tagId ?? searchState.tagId,
      page: overrides.page ?? notesPage.page,
      pageSize: overrides.pageSize ?? notesPage.pageSize,
    };
    const data = await listNotes({
      q: nextState.query,
      sort: nextState.sort,
      tag_id: nextState.tagId,
      page: nextState.page,
      page_size: nextState.pageSize,
    });
    setNotesPage(toPageState(data, notesPage.pageSize));
  }

  async function refreshTags() {
    const data = await listTags();
    setAvailableTags(data);
  }

  async function refreshActions(nextFilter = actionFilter) {
    const data = await listActionItems({
      completed: nextFilter,
      page: 1,
      page_size: actionsPage.pageSize,
    });
    setActionsPage(toPageState(data, actionsPage.pageSize));
  }

  useEffect(() => {
    refreshNotes().catch((error) => setStatusMessage(error.message));
    refreshTags().catch((error) => setStatusMessage(error.message));
    refreshActions().catch((error) => setStatusMessage(error.message));
  }, []);

  async function handleCreateNote(event) {
    event.preventDefault();
    await createNote(noteDraft);
    setNoteDraft({ title: '', content: '' });
    setStatusMessage('');
    await refreshNotes({ page: 1 });
  }

  async function handleCreateTag(event) {
    event.preventDefault();
    if (!tagDraft.trim()) {
      return;
    }
    await createTag({ name: tagDraft });
    setTagDraft('');
    await refreshTags();
  }

  async function handleEditNote(note) {
    const nextTitle = window.prompt('Edit title', note.title);
    if (nextTitle === null) {
      return;
    }
    const nextContent = window.prompt('Edit content', note.content);
    if (nextContent === null) {
      return;
    }

    const previousItems = notesPage.items;
    setNotesPage((current) => ({
      ...current,
      items: current.items.map((item) =>
        item.id === note.id ? { ...item, title: nextTitle, content: nextContent } : item,
      ),
    }));

    try {
      const updated = await updateNote(note.id, { title: nextTitle, content: nextContent });
      setNotesPage((current) => ({
        ...current,
        items: current.items.map((item) => (item.id === note.id ? updated : item)),
      }));
      setStatusMessage('');
    } catch (error) {
      setNotesPage((current) => ({ ...current, items: previousItems }));
      setStatusMessage(`Edit failed: ${error.message}`);
    }
  }

  async function handleDeleteNote(noteId) {
    const previousItems = notesPage.items;
    setNotesPage((current) => ({
      ...current,
      items: current.items.filter((item) => item.id !== noteId),
      total: Math.max(0, current.total - 1),
    }));

    try {
      await deleteNote(noteId);
      setStatusMessage('');
      await refreshNotes();
    } catch (error) {
      setNotesPage((current) => ({ ...current, items: previousItems, total: current.total + 1 }));
      setStatusMessage(`Delete failed: ${error.message}`);
    }
  }

  async function handleExtractNote(noteId) {
    await extractNote(noteId, true);
    await Promise.all([refreshNotes(), refreshTags(), refreshActions()]);
  }

  async function handleSearchSubmit(event) {
    event.preventDefault();
    await refreshNotes({ page: 1 });
  }

  function handleSearchChange(field, value) {
    setSearchState((current) => ({ ...current, [field]: value }));
  }

  async function handlePageChange(nextPage) {
    if (nextPage < 1) {
      return;
    }
    await refreshNotes({ page: nextPage });
  }

  async function handleTagFilterChange(tagId) {
    setSearchState((current) => ({ ...current, tagId }));
    await refreshNotes({ page: 1, tagId });
  }

  async function handleCreateActionItem(event) {
    event.preventDefault();
    await createActionItem({ description: actionDraft });
    setActionDraft('');
    await refreshActions();
  }

  function handleToggleSelected(itemId) {
    setSelectedIds((current) => {
      const next = new Set(current);
      if (next.has(itemId)) {
        next.delete(itemId);
      } else {
        next.add(itemId);
      }
      return next;
    });
  }

  async function handleFilterChange(filterValue) {
    setActionFilter(filterValue);
    setSelectedIds(new Set());
    await refreshActions(filterValue);
  }

  async function handleCompleteItem(itemId) {
    await completeActionItem(itemId);
    await refreshActions();
  }

  async function handleBulkComplete() {
    if (selectedIds.size === 0) {
      return;
    }
    await bulkCompleteActionItems(Array.from(selectedIds));
    setSelectedIds(new Set());
    await refreshActions();
  }

  return (
    <main className="app-shell">
      <header className="hero">
        <p className="eyebrow">Week 5</p>
        <h1>Agentic Workspace</h1>
        <p className="hero-copy">FastAPI + React playground for notes, tags, extraction, and action-item workflows.</p>
      </header>
      <div className="panel-grid">
        <NotesPanel
          noteDraft={noteDraft}
          tagDraft={tagDraft}
          notesPage={notesPage}
          searchState={searchState}
          availableTags={availableTags}
          onNoteDraftChange={(field, value) => setNoteDraft((current) => ({ ...current, [field]: value }))}
          onTagDraftChange={setTagDraft}
          onCreateNote={handleCreateNote}
          onCreateTag={handleCreateTag}
          onSearchSubmit={handleSearchSubmit}
          onSearchChange={handleSearchChange}
          onPageChange={handlePageChange}
          onTagFilterChange={handleTagFilterChange}
          onEditNote={handleEditNote}
          onDeleteNote={handleDeleteNote}
          onExtractNote={handleExtractNote}
          statusMessage={statusMessage}
        />
        <ActionItemsPanel
          draftDescription={actionDraft}
          itemsPage={actionsPage}
          selectedIds={selectedIds}
          activeFilter={actionFilter}
          onDraftChange={setActionDraft}
          onCreateItem={handleCreateActionItem}
          onToggleSelected={handleToggleSelected}
          onFilterChange={handleFilterChange}
          onCompleteItem={handleCompleteItem}
          onBulkComplete={handleBulkComplete}
        />
      </div>
    </main>
  );
}
