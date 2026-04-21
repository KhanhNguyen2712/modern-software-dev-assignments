# Task 08 - List endpoint pagination for all collections

## What I changed

- Added paginated response payloads for:
  - `GET /notes/`
  - `GET /action-items/`
- Standardized the list payload shape under the task 7 envelope:
  - `{ "ok": true, "data": { "items": [...], "total": n, "page": p, "page_size": s } }`
- Added request validation on `page` and `page_size` using FastAPI query constraints.
- Enforced a maximum `page_size` of `100` so oversize requests fail with the existing validation envelope.
- Updated the backend schemas with a reusable `PaginatedData[T]` model.

## Tests added or updated

- Updated `backend/tests/test_notes.py` to verify:
  - default list pagination metadata
  - page 2 behavior
  - empty last page behavior
  - rejection of oversized `page_size`
- Updated `backend/tests/test_action_items.py` with the same coverage for action item lists.

## Verification

- `conda run -n cs146s make test`
- `conda run -n cs146s make lint`

Both commands passed before the task was committed.
