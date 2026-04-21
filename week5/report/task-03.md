# Task 03 - Full Notes CRUD with optimistic UI updates

## What I changed

- Added `PUT /notes/{id}` to update an existing note.
- Added `DELETE /notes/{id}` to remove an existing note.
- Reused the validation added earlier so note updates also enforce non-empty, bounded payloads.
- Added a `DeleteResult` response payload and kept the task 7 envelope format consistent.
- Updated the existing frontend to support:
  - inline edit via prompts
  - delete actions
  - optimistic UI updates for both edit and delete
  - rollback on failed requests with an error message shown in the UI

## Tests added or updated

- Expanded `backend/tests/test_notes.py` to cover:
  - successful note update
  - successful note deletion
  - `404 NOT_FOUND` behavior for update/delete on a missing note

## Verification

- `conda run -n cs146s make test`
- `conda run -n cs146s make lint`

Both commands passed before the task was committed.
