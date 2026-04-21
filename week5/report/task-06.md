# Task 06 - Improve extraction logic and endpoints

## What I changed

- Extended `backend/app/services/extract.py` to parse:
  - hashtags like `#Launch`
  - checklist action items like `- [ ] Ship release`
- Kept support for the earlier action-item heuristics as well.
- Added `POST /notes/{id}/extract` with an `apply=true|false` flow:
  - preview extraction results without changing data
  - persist extracted tags and action items when `apply=true`
- When `apply=true`:
  - tags are created if needed
  - tags are attached to the note
  - action items are persisted as new rows

## Tests added or updated

- Expanded `backend/tests/test_extract.py` to cover:
  - hashtag parsing
  - structured extraction preview
  - the `apply=true` persistence path for tags and action items

## Verification

- `conda run -n cs146s make test`
- `conda run -n cs146s make lint`

Both commands passed before the task was committed.
