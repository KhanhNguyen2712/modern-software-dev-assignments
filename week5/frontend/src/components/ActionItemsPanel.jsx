export function ActionItemsPanel({
  draftDescription,
  itemsPage,
  selectedIds,
  activeFilter,
  onDraftChange,
  onCreateItem,
  onToggleSelected,
  onFilterChange,
  onCompleteItem,
  onBulkComplete,
}) {
  return (
    <section className="panel">
      <h2>Action Items</h2>
      <div className="button-row">
        <button type="button" className={activeFilter === null ? 'active-filter' : ''} onClick={() => onFilterChange(null)}>
          All
        </button>
        <button type="button" className={activeFilter === false ? 'active-filter' : ''} onClick={() => onFilterChange(false)}>
          Open
        </button>
        <button type="button" className={activeFilter === true ? 'active-filter' : ''} onClick={() => onFilterChange(true)}>
          Done
        </button>
        <button type="button" onClick={onBulkComplete}>
          Complete Selected
        </button>
      </div>
      <form className="inline-form" onSubmit={onCreateItem}>
        <input
          aria-label="Action description"
          value={draftDescription}
          onChange={(event) => onDraftChange(event.target.value)}
          placeholder="Description"
          required
        />
        <button type="submit">Add</button>
      </form>
      <ul className="card-list">
        {itemsPage.items.map((item) => (
          <li className="card-list-item" key={item.id}>
            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={selectedIds.has(item.id)}
                onChange={() => onToggleSelected(item.id)}
              />
              <span>{item.description}</span>
            </label>
            <div className="button-row">
              <span>{item.completed ? 'done' : 'open'}</span>
              {!item.completed && (
                <button type="button" onClick={() => onCompleteItem(item.id)}>
                  Complete
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
