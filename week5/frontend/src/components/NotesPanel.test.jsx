import { fireEvent, render, screen } from '@testing-library/react';

import { NotesPanel } from './NotesPanel';

test('renders note count and tags for listed notes', () => {
  render(
    <NotesPanel
      noteDraft={{ title: '', content: '' }}
      notesPage={{ items: [{ id: 1, title: 'Alpha', content: 'Body', tags: [{ id: 2, name: 'launch' }] }], total: 1, page: 1, pageSize: 5 }}
      searchState={{ query: '', sort: 'created_desc', tagId: null }}
      availableTags={[{ id: 2, name: 'launch' }]}
      onNoteDraftChange={() => {}}
      onCreateNote={(event) => event.preventDefault()}
      onSearchSubmit={(event) => event.preventDefault()}
      onSearchChange={() => {}}
      onPageChange={() => {}}
      onTagFilterChange={() => {}}
      onEditNote={() => {}}
      onDeleteNote={() => {}}
      statusMessage=""
    />,
  );

  expect(screen.getByText('Showing 1 of 1 result(s)')).toBeInTheDocument();
  expect(screen.getAllByText('#launch')).toHaveLength(2);
});

test('calls page change handler from pagination controls', () => {
  const handlePageChange = vi.fn();

  render(
    <NotesPanel
      noteDraft={{ title: '', content: '' }}
      notesPage={{ items: [{ id: 1, title: 'Alpha', content: 'Body', tags: [] }], total: 10, page: 1, pageSize: 5 }}
      searchState={{ query: '', sort: 'created_desc', tagId: null }}
      availableTags={[]}
      onNoteDraftChange={() => {}}
      onCreateNote={(event) => event.preventDefault()}
      onSearchSubmit={(event) => event.preventDefault()}
      onSearchChange={() => {}}
      onPageChange={handlePageChange}
      onTagFilterChange={() => {}}
      onEditNote={() => {}}
      onDeleteNote={() => {}}
      statusMessage=""
    />,
  );

  fireEvent.click(screen.getByText('Next'));

  expect(handlePageChange).toHaveBeenCalledWith(2);
});
