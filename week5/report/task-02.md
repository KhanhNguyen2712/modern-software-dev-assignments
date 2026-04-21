# Task 02 - Notes search with pagination and sorting

## What I changed

- Reworked `GET /notes/search` to support:
  - `q`
  - `page`
  - `page_size`
  - `sort=created_desc|title_asc`
- Implemented case-insensitive matching on note title and content.
- Returned paginated search results in the envelope shape:
  - `{ "ok": true, "data": { "items": [...], "total": n, "page": p, "page_size": s } }`
- Added query composition for filtering, sorting, and pagination in the notes router.
- Updated the existing frontend to support:
  - note search input
  - sort selection
  - result count
  - next/previous pagination controls

## Tests added or updated

- Expanded `backend/tests/test_notes.py` to cover:
  - case-insensitive search
  - `title_asc` sorting
  - `created_desc` sorting
  - paginated search results
  - invalid sort rejection

## Verification

- `conda run -n cs146s make test`
- `conda run -n cs146s make lint`

Both commands passed before the task was committed.
