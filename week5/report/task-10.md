# Task 10 - Test coverage improvements

## What I changed

- Added backend error-path coverage in `backend/tests/test_api_errors.py` for:
  - invalid note/search/update requests
  - missing note/tag extract and attach/detach cases
  - invalid and missing action item operations
  - duplicate/invalid/missing tag operations
- Added an extra stability test for repeated bulk-complete requests.
- Added frontend integration-style tests in `frontend/src/App.test.jsx` covering:
  - search request wiring
  - notes pagination request wiring
  - optimistic delete rollback on API failure

## Verification

- `conda run -n cs146s make test`
- `conda run -n cs146s make lint`
- `cd week5/frontend && npm test`
- `cd week5/frontend && npm run build`

All commands passed before the task was committed.
