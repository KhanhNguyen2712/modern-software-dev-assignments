# Task 04 - Action items filters and bulk complete

## What I changed

- Extended `GET /action-items/` with an optional `completed=true|false` filter.
- Added `POST /action-items/bulk-complete` to complete multiple action items in one request.
- Implemented bulk-complete with transactional safety by validating all IDs before mutating any rows.
- Updated the existing frontend to support:
  - filter buttons for all/open/done action items
  - checkbox selection
  - a bulk complete action for selected items

## Tests added or updated

- Expanded `backend/tests/test_action_items.py` to cover:
  - filtered listing by completion state
  - successful bulk completion
  - rollback behavior when any requested ID is missing

## Verification

- `conda run -n cs146s make test`
- `conda run -n cs146s make lint`

Both commands passed before the task was committed.
