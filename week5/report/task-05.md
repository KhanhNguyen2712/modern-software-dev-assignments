# Task 05 - Tags feature with many-to-many relation

## What I changed

- Added a new `Tag` model and a `note_tags` join table for the many-to-many note/tag relationship.
- Updated note responses so each note now includes its attached tags.
- Added tag endpoints:
  - `GET /tags/`
  - `POST /tags/`
  - `DELETE /tags/{id}`
- Added note/tag relation endpoints:
  - `POST /notes/{id}/tags`
  - `DELETE /notes/{id}/tags/{tag_id}`
- Extended note listing and note search to support filtering by `tag_id`.
- Updated the frontend to:
  - render note tags as chips
  - list available tags as filter buttons
  - create tags from the UI

## Tests added or updated

- Added `backend/tests/test_tags.py` to cover:
  - tag creation and listing
  - tag attach/detach on notes
  - filtering notes by tag
  - not-found behavior for missing tags or notes

## Verification

- `conda run -n cs146s make test`
- `conda run -n cs146s make lint`

Both commands passed before the task was committed.
