# Week 4 — Developer Command Center

This directory contains a full-stack starter app: FastAPI backend with SQLite (SQLAlchemy) and a static HTML/JS frontend.

## Project Structure
- `backend/app/main.py` — FastAPI app entry point, mounts static files and routers
- `backend/app/models.py` — SQLAlchemy models: `Note`, `ActionItem`
- `backend/app/schemas.py` — Pydantic request/response schemas
- `backend/app/db.py` — Database engine, session management (`get_db`), and seeding
- `backend/app/routers/notes.py` — Notes CRUD endpoints (GET list, GET search, GET by-id, POST create)
- `backend/app/routers/action_items.py` — Action items endpoints (GET list, POST create, PUT complete)
- `backend/app/services/extract.py` — Text extraction utility (parses TODOs and action items)
- `backend/tests/conftest.py` — Test fixtures (creates a temp SQLite DB per test)
- `backend/tests/test_notes.py` — Tests for notes endpoints
- `backend/tests/test_action_items.py` — Tests for action items endpoints
- `backend/tests/test_extract.py` — Tests for extract service
- `frontend/index.html` — Main HTML page
- `frontend/app.js` — Frontend JavaScript (fetches from API, renders notes/actions)
- `frontend/styles.css` — Styles
- `data/seed.sql` — Initial seed data (inserted on first run)
- `data/app.db` — SQLite database file
- `docs/TASKS.md` — Outstanding improvement tasks

## How to Run (from this directory)
- Start server: `make run` → http://localhost:8000
- Run tests: `make test`
- Format code: `make format`
- Lint code: `make lint`
- API docs: http://localhost:8000/docs

## Coding Conventions
- Use Pydantic schemas for ALL request/response bodies
- Use SQLAlchemy ORM (not raw SQL) for database queries
- Return proper HTTP status codes: 201 for create, 200 for success, 404 for not found, 400 for bad input
- All router endpoints get DB sessions via `Depends(get_db)`
- Tests use the `client` fixture from `conftest.py` (creates a fresh temp SQLite DB)

## Code Style
- Formatter: `black`
- Linter: `ruff`
- Always run `make format` before committing

## Safe Commands (run without asking)
- `make run`, `make test`, `make format`, `make lint`, `make seed`
- `pytest` with any flags
- `ruff check`

## Unsafe Commands (ask before running)
- `pip install` or any dependency changes
- Database migrations or destructive DB operations
- `git push`

## Workflow: Adding a New API Endpoint
1. First, write a failing test in `backend/tests/test_*.py`
2. Implement the endpoint in `backend/app/routers/*.py`
3. If needed, add/update Pydantic schemas in `backend/app/schemas.py`
4. Run `make test` to verify all tests pass
5. Run `make format` to fix code style
6. Update `docs/TASKS.md` if completing a listed task

## Current App Status
- Notes: GET (list, search, by-id), POST (create) — working
- Action Items: GET (list), POST (create), PUT (complete) — working
- Missing: PUT/DELETE for notes, request validation, tag extraction, API docs
