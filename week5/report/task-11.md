# Task 11 - Deployable on Vercel

## What I changed

- Added `frontend/package.json` and `frontend/vite.config.js` earlier in task 1 so the frontend now has:
  - `build`
  - `preview`
  - `dev`
  - `test`
- Added `api/index.py` to expose the FastAPI app for Vercel's Python runtime.
- Added `vercel.json` with:
  - a frontend build command
  - `outputDirectory` pointing to `frontend/dist`
  - a rewrite for `/api/*` to the Python entrypoint
- Added `requirements.txt` for the Python function runtime.
- Added CORS configuration in `backend/app/main.py` driven by:
  - `CORS_ORIGINS`
  - `VERCEL_FRONTEND_ORIGIN`
- Updated `week5/README.md` with a deploy guide, environment variables, build commands, and rollback notes.

## Verification

- `conda run -n cs146s make test`
- `conda run -n cs146s make lint`
- `cd week5/frontend && npm test`
- `cd week5/frontend && npm run build`

All commands passed before the task was committed.
