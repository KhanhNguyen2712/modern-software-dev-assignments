# Task 07 - Robust error handling and response envelopes

## What I changed

- Added schema-based validation for note titles, note content, and action item descriptions in `backend/app/schemas.py`.
- Introduced consistent API envelopes:
  - success: `{ "ok": true, "data": ... }`
  - error: `{ "ok": false, "error": { "code": "...", "message": "..." } }`
- Added reusable response helpers in `backend/app/responses.py`.
- Updated note and action item routes to return success envelopes.
- Added FastAPI exception handlers in `backend/app/main.py` for:
  - `404 NOT_FOUND`
  - `400 VALIDATION_ERROR`
  - `500 INTERNAL_SERVER_ERROR`
- Replaced deprecated class-based Pydantic config with `ConfigDict`.
- Replaced deprecated startup event usage with a lifespan handler.

## Tests added or updated

- Updated `backend/tests/test_notes.py` to verify:
  - success envelope on create/list
  - `NOT_FOUND` envelope for missing note
  - `VALIDATION_ERROR` envelope for invalid payloads
- Updated `backend/tests/test_action_items.py` to verify:
  - success envelope on create/complete/list
  - `NOT_FOUND` envelope for missing action item

## Verification

- `conda run -n cs146s make test`
- `conda run -n cs146s make lint`

Both commands passed before the task was committed.
