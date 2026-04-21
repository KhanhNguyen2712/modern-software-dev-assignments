# Task 09 - Query performance and indexes

## What I changed

- Added an index on `notes.title`.
- Added dedicated indexes on the tag join table:
  - `note_tags.note_id`
  - `note_tags.tag_id`
- Kept the existing primary-key indexes in place and added the extra indexes needed for common note/tag lookup paths.

## Tests added or updated

- Added `backend/tests/test_performance.py` to verify:
  - the expected SQLite indexes exist
  - `EXPLAIN QUERY PLAN` for note title lookup uses an index

## Verification

- `conda run -n cs146s make test`
- `conda run -n cs146s make lint`

Both commands passed before the task was committed.
