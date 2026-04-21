import { fireEvent, render, screen } from '@testing-library/react';

import { ActionItemsPanel } from './ActionItemsPanel';

test('renders action items and filter controls', () => {
  render(
    <ActionItemsPanel
      draftDescription=""
      itemsPage={{ items: [{ id: 1, description: 'Ship', completed: false }], total: 1, page: 1, pageSize: 10 }}
      selectedIds={new Set()}
      activeFilter={null}
      onDraftChange={() => {}}
      onCreateItem={(event) => event.preventDefault()}
      onToggleSelected={() => {}}
      onFilterChange={() => {}}
      onCompleteItem={() => {}}
      onBulkComplete={() => {}}
    />,
  );

  expect(screen.getByText('Complete Selected')).toBeInTheDocument();
  expect(screen.getByText('Ship')).toBeInTheDocument();
});

test('triggers bulk complete handler', () => {
  const handleBulkComplete = vi.fn();

  render(
    <ActionItemsPanel
      draftDescription=""
      itemsPage={{ items: [{ id: 1, description: 'Ship', completed: false }], total: 1, page: 1, pageSize: 10 }}
      selectedIds={new Set([1])}
      activeFilter={null}
      onDraftChange={() => {}}
      onCreateItem={(event) => event.preventDefault()}
      onToggleSelected={() => {}}
      onFilterChange={() => {}}
      onCompleteItem={() => {}}
      onBulkComplete={handleBulkComplete}
    />,
  );

  fireEvent.click(screen.getByText('Complete Selected'));

  expect(handleBulkComplete).toHaveBeenCalled();
});
