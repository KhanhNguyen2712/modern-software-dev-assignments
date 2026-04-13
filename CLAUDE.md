# Repository Guidance

This repository contains weekly assignments. For Week 4 tasks, scope all implementation and verification to `week4/` unless explicitly requested otherwise.

## Week 4 Quick Commands
- Run app: `cd week4 && make run`
- Run tests: `cd week4 && make test`
- Format code: `cd week4 && make format`
- Lint code: `cd week4 && make lint`

## Code Map (Week 4)
- API app: `week4/backend/app/main.py`
- Routers: `week4/backend/app/routers/`
- Schemas: `week4/backend/app/schemas.py`
- DB models: `week4/backend/app/models.py`
- Extraction service: `week4/backend/app/services/extract.py`
- Tests: `week4/backend/tests/`
- Frontend: `week4/frontend/`
- Tasks and docs: `week4/docs/TASKS.md`, `week4/docs/API.md`

## Safety and Quality Guardrails
- Prefer test-first updates: add/update tests before finalizing implementation.
- After code changes, run targeted pytest first, then full test suite.
- Keep changes minimal and avoid unrelated refactors.
- Do not run destructive git commands.

## Workflow Snippet: Add or Change Endpoint
1. Add/adjust failing tests in `week4/backend/tests/`.
2. Implement route/schema/service changes.
3. Update frontend if endpoint is user-facing.
4. Run `make test` and `make lint` in `week4/`.
5. Update `week4/docs/API.md` to prevent docs drift.
