# Project: Developer Command Center

## Stack
- Backend: FastAPI + SQLite (SQLAlchemy)
- Frontend: Static HTML/JS/CSS
- Tests: pytest
- Linting: black + ruff

## How to Run
- Activate env: `conda activate cs146s`
- Start: `make run` (từ thư mục week4/)
- Frontend: http://localhost:8000
- API docs: http://localhost:8000/docs

## Project Structure
- `backend/app/routers/action_items.py` → CRUD cho ActionItem
- `backend/app/routers/notes.py`        → CRUD cho Note
- `backend/app/services/db.py`          → DB session
- `backend/app/services/extract.py`     → Extract/parsing logic
- `backend/app/models.py`               → SQLAlchemy models (Note, ActionItem)
- `backend/app/schemas.py`              → Pydantic schemas
- `backend/app/main.py`                 → FastAPI entry point
- `backend/tests/`                      → pytest tests
- `data/seed.sql`                       → Seed data
- `docs/TASKS.md`                       → Task list

## Models hiện có
- Note: id, title (String 200), content (Text)
- ActionItem: id, description (Text), completed (Boolean)

## Schemas hiện có
- NoteCreate, NoteRead
- ActionItemCreate, ActionItemRead

## Import pattern (dùng đúng trong mọi router)
```python
from ..db import get_db
from ..models import Note, ActionItem
from ..schemas import NoteCreate, NoteRead
```

## Coding Rules
- Viết test trước (TDD), sau đó implement
- Luôn chạy `make format && make lint` trước commit
- Không xóa seed data không có backup
- Router mới phải đăng ký trong main.py

## Workflow thêm endpoint
1. Viết failing test trong backend/tests/
2. Implement trong backend/app/routers/
3. Nếu cần schema mới: thêm vào schemas.py
4. make test → xanh
5. make format && make lint
6. Commit
EOF