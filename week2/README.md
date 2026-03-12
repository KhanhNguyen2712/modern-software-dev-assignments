# Week 2 Action Item Extractor

This project is a small FastAPI + SQLite application that converts free-form notes into action items. It supports both the original heuristic extractor and an Ollama-backed LLM extractor, persists notes and action items, and includes a minimal frontend for manual testing.

## Features

- Create and store notes in SQLite.
- Extract action items with rule-based heuristics.
- Extract action items with an Ollama model using structured JSON output.
- Mark extracted action items as done.
- List all saved notes from the frontend or API.

## Project Structure

- `week2/app/main.py`: FastAPI app entrypoint and startup lifecycle.
- `week2/app/routers/`: API routes for notes and action items.
- `week2/app/services/extract.py`: Heuristic and LLM extraction logic.
- `week2/app/db.py`: SQLite access layer.
- `week2/frontend/index.html`: Minimal frontend UI.
- `week2/tests/test_extract.py`: Unit tests for extraction logic.

## Setup

1. Activate your Python environment.
2. Install dependencies from the repo root:

```bash
poetry install
```

3. Make sure Ollama is installed and running if you want to use the LLM endpoint.
4. Pull a small model, for example:

```bash
ollama pull llama3.2:3b
```

5. Optionally configure a different model:

```bash
$env:OLLAMA_MODEL="llama3.2:3b"
```

## Run The App

From the project root:

```bash
poetry run uvicorn week2.app.main:app --reload
```

Then open `http://127.0.0.1:8000/`.

## API Endpoints

- `GET /`: Serve the frontend.
- `POST /notes`: Create a note.
- `GET /notes`: List all saved notes.
- `GET /notes/{note_id}`: Fetch one note.
- `POST /action-items/extract`: Extract action items with heuristics.
- `POST /action-items/extract-llm`: Extract action items with Ollama.
- `GET /action-items`: List action items, optionally filtered by `note_id`.
- `POST /action-items/{action_item_id}/done`: Mark an action item done or undone.

### Example Request

```bash
curl -X POST http://127.0.0.1:8000/action-items/extract-llm \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"TODO: email the client\n- [ ] write tests\",\"save_note\":true}"
```

## Run Tests

Run the extraction test suite from the repo root:

```bash
poetry run pytest week2/tests
```

The LLM unit tests mock the Ollama client, so they do not require a live Ollama server.
