import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import App from './App';
import * as api from './api';

vi.mock('./api', () => ({
  bulkCompleteActionItems: vi.fn(),
  completeActionItem: vi.fn(),
  createActionItem: vi.fn(),
  createNote: vi.fn(),
  createTag: vi.fn(),
  deleteNote: vi.fn(),
  extractNote: vi.fn(),
  listActionItems: vi.fn(),
  listNotes: vi.fn(),
  listTags: vi.fn(),
  updateNote: vi.fn(),
}));

function resolvedPage(items, total = items.length, page = 1, page_size = 5) {
  return { items, total, page, page_size };
}

beforeEach(() => {
  vi.clearAllMocks();
  api.listTags.mockResolvedValue([]);
  api.listActionItems.mockResolvedValue(resolvedPage([], 0, 1, 10));
  api.listNotes.mockResolvedValue(resolvedPage([], 0));
  api.deleteNote.mockResolvedValue({ deleted: true });
});

test('submits search through the notes API contract', async () => {
  api.listNotes
    .mockResolvedValueOnce(resolvedPage([{ id: 1, title: 'First', content: 'Body', tags: [] }], 6, 1, 5))
    .mockResolvedValueOnce(resolvedPage([{ id: 2, title: 'Found', content: 'Body', tags: [] }], 1, 1, 5));

  render(<App />);

  await screen.findByText('First');

  fireEvent.change(screen.getByLabelText('Search notes'), { target: { value: 'Found' } });
  fireEvent.click(screen.getByText('Search'));

  await waitFor(() =>
    expect(api.listNotes).toHaveBeenLastCalledWith({
      q: 'Found',
      sort: 'created_desc',
      tag_id: null,
      page: 1,
      page_size: 5,
    }),
  );
});

test('uses pagination controls to request the next notes page', async () => {
  api.listNotes
    .mockResolvedValueOnce(resolvedPage([{ id: 1, title: 'First', content: 'Body', tags: [] }], 9, 1, 5))
    .mockResolvedValueOnce(resolvedPage([{ id: 3, title: 'Next', content: 'Body', tags: [] }], 9, 2, 5));

  render(<App />);

  await screen.findByText('First');

  fireEvent.click(screen.getByText('Next'));

  await waitFor(() =>
    expect(api.listNotes).toHaveBeenLastCalledWith({
      q: '',
      sort: 'created_desc',
      tag_id: null,
      page: 2,
      page_size: 5,
    }),
  );
});

test('rolls back optimistic delete when the API request fails', async () => {
  api.listNotes.mockImplementation(async () =>
    resolvedPage([{ id: 1, title: 'Keep me', content: 'Body', tags: [] }], 1, 1, 5),
  );
  api.deleteNote.mockRejectedValue(new Error('Delete exploded'));

  render(<App />);

  await screen.findByText('Keep me');

  fireEvent.click(screen.getByText('Delete'));

  expect(screen.queryByText('Keep me')).not.toBeInTheDocument();

  await waitFor(() => expect(screen.getByText('Keep me')).toBeInTheDocument());
  expect(screen.getByText('Delete failed: Delete exploded')).toBeInTheDocument();
});
