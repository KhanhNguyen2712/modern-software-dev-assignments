function NoteCard({ note, onEditNote, onDeleteNote, onExtractNote }) {
  return (
    <li className="card-list-item">
      <div className="note-copy">
        <strong>{note.title}</strong>
        <p>{note.content}</p>
        <div className="chip-row">
          {note.tags.map((tag) => (
            <span className="tag-chip" key={tag.id}>
              #{tag.name}
            </span>
          ))}
        </div>
      </div>
      <div className="button-row">
        <button type="button" onClick={() => onEditNote(note)}>
          Edit
        </button>
        <button type="button" onClick={() => onDeleteNote(note.id)}>
          Delete
        </button>
        <button type="button" onClick={() => onExtractNote(note.id)}>
          Extract
        </button>
      </div>
    </li>
  );
}

export function NotesPanel({
  noteDraft,
  tagDraft,
  notesPage,
  searchState,
  availableTags,
  onNoteDraftChange,
  onTagDraftChange,
  onCreateNote,
  onCreateTag,
  onSearchSubmit,
  onSearchChange,
  onPageChange,
  onTagFilterChange,
  onEditNote,
  onDeleteNote,
  onExtractNote,
  statusMessage,
}) {
  const totalPages = Math.max(1, Math.ceil(notesPage.total / notesPage.pageSize));

  return (
    <section className="panel">
      <h2>Notes</h2>
      <p className="status-copy" aria-live="polite">
        {statusMessage}
      </p>
      <div className="chip-row">
        <button type="button" onClick={() => onTagFilterChange(null)}>
          All tags
        </button>
        {availableTags.map((tag) => (
          <button key={tag.id} type="button" onClick={() => onTagFilterChange(tag.id)}>
            #{tag.name}
          </button>
        ))}
      </div>
      <form className="inline-form" onSubmit={onSearchSubmit}>
        <input
          aria-label="Search notes"
          value={searchState.query}
          onChange={(event) => onSearchChange('query', event.target.value)}
          placeholder="Search notes"
        />
        <select
          aria-label="Sort notes"
          value={searchState.sort}
          onChange={(event) => onSearchChange('sort', event.target.value)}
        >
          <option value="created_desc">Newest first</option>
          <option value="title_asc">Title A-Z</option>
        </select>
        <button type="submit">Search</button>
      </form>
      <p>Showing {notesPage.items.length} of {notesPage.total} result(s)</p>
      <form className="stacked-form" onSubmit={onCreateNote}>
        <input
          aria-label="Note title"
          value={noteDraft.title}
          onChange={(event) => onNoteDraftChange('title', event.target.value)}
          placeholder="Title"
          required
        />
        <textarea
          aria-label="Note content"
          value={noteDraft.content}
          onChange={(event) => onNoteDraftChange('content', event.target.value)}
          placeholder="Content"
          required
        />
        <button type="submit">Add note</button>
      </form>
      <ul className="card-list">
        {notesPage.items.map((note) => (
          <NoteCard
            key={note.id}
            note={note}
            onEditNote={onEditNote}
            onDeleteNote={onDeleteNote}
            onExtractNote={onExtractNote}
          />
        ))}
      </ul>
      <div className="button-row">
        <button type="button" onClick={() => onPageChange(notesPage.page - 1)} disabled={notesPage.page <= 1}>
          Prev
        </button>
        <span>
          Page {notesPage.page} of {totalPages}
        </span>
        <button
          type="button"
          onClick={() => onPageChange(notesPage.page + 1)}
          disabled={notesPage.page >= totalPages}
        >
          Next
        </button>
      </div>
      <form className="inline-form" onSubmit={onCreateTag}>
        <input
          aria-label="Create tag"
          value={tagDraft}
          onChange={(event) => onTagDraftChange(event.target.value)}
          placeholder="Create tag"
        />
        <button type="submit">Add Tag</button>
      </form>
    </section>
  );
}
