# Week 5

Minimal full‑stack starter for experimenting with autonomous coding agents.

- FastAPI backend with SQLite (SQLAlchemy)
- Static frontend (no Node toolchain needed)
- Minimal tests (pytest)
- Pre-commit (black + ruff)
- Tasks to practice agent-driven workflows

## Quickstart

1) Create and activate a virtualenv, then install dependencies

```bash
cd /Users/mihaileric/Documents/code/modern-software-dev-assignments
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

2) (Optional) Install pre-commit hooks

```bash
pre-commit install
```

3) Run the app (from `week5/`)

```bash
cd week5 && make run
```

Open `http://localhost:8000` for the frontend and `http://localhost:8000/docs` for the API docs.

## Structure

```
backend/                # FastAPI app
frontend/               # Static UI served by FastAPI
data/                   # SQLite DB + seed
docs/                   # TASKS for agent-driven workflows
```

## Tests

```bash
cd week5 && make test
```

## Formatting/Linting

```bash
cd week5 && make format
cd week5 && make lint
```

## Configuration

Copy `.env.example` to `.env` (in `week5/`) to override defaults like the database path.

## Deploy on Vercel

This repo now includes a Vercel setup for a static React frontend plus a Python FastAPI function.

### Files

- `frontend/package.json` and `frontend/vite.config.js`
- `api/index.py`
- `vercel.json`
- `requirements.txt`

### Recommended Vercel project settings

1. Set the project root to `week5/`.
2. Leave build settings to the repo config in `vercel.json`.
3. Set `VITE_API_BASE_URL=/api` if you are deploying the frontend and FastAPI function in the same Vercel project.
4. If the frontend talks to an external backend instead, set `VITE_API_BASE_URL` to the full backend URL and configure:
   - `VERCEL_FRONTEND_ORIGIN=https://<your-frontend-domain>`
   - or `CORS_ORIGINS=https://<your-frontend-domain>`

### Build and local verification

```bash
cd week5/frontend && npm install
cd week5/frontend && npm run build
cd week5 && conda run -n cs146s make test
```

### Rollback

- In the Vercel dashboard, promote the previous successful deployment.
- If you changed environment variables, restore the previous values and redeploy.
