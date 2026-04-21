# Task 01 - Migrate frontend to Vite + React

## What I changed

- Replaced the old static HTML/JS entrypoint with a Vite + React frontend in `week5/frontend/`.
- Added:
  - `package.json`
  - `vite.config.js`
  - React entrypoint and component structure under `frontend/src/`
- Migrated the existing UI flows into React:
  - notes list/create/edit/delete
  - notes search, pagination, tag filters, extract action
  - action item list/create/complete
  - action item filters and bulk complete
  - tag creation
- Updated FastAPI to serve the built Vite bundle:
  - mount `/assets` from `frontend/dist/assets`
  - serve `/` from `frontend/dist/index.html`
- Updated `Makefile` with:
  - `web-install`
  - `web-dev`
  - `web-build`
  - `make run` now builds the frontend bundle first

## Tests added or updated

- Added React component tests with Vitest + React Testing Library for:
  - `NotesPanel`
  - `ActionItemsPanel`
- Kept the existing backend integration tests in place for API compatibility.

## Verification

- `conda run -n cs146s make test`
- `conda run -n cs146s make lint`
- `cd week5/frontend && npm test`
- `cd week5/frontend && npm run build`
- `conda run -n cs146s env PYTHONPATH=. python -c "from fastapi.testclient import TestClient; from backend.app.main import app; client = TestClient(app); response = client.get('/'); print(response.status_code); print('/assets/' in response.text)"`

All commands passed before the task was committed.
