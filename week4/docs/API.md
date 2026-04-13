# Week 4 API Reference

Base URL: `http://localhost:8000`

## Health/UI

### `GET /`
- Description: Serves the static frontend page.
- Response: `200 OK` with `frontend/index.html`.

## Notes

### `GET /notes/`
- Description: List all notes.
- Response: `200 OK`
- Body:
```json
[
  { "id": 1, "title": "Welcome", "content": "..." }
]
```

### `POST /notes/`
- Description: Create a note.
- Request body:
```json
{ "title": "My title", "content": "My content" }
```
- Validation:
  - `title`: required, min length 1, max length 200
  - `content`: required, min length 1
- Responses:
  - `201 Created` with created note payload
  - `422 Unprocessable Entity` on validation failure

### `GET /notes/search/?q=<query>`
- Description: Search notes by title/content (case-insensitive contains).
- Query parameter:
  - `q` optional. If omitted, returns all notes.
- Response: `200 OK` with note list.

### `GET /notes/{note_id}`
- Description: Fetch a note by id.
- Responses:
  - `200 OK` with note payload
  - `404 Not Found` with `{ "detail": "Note not found" }`

### `PUT /notes/{note_id}`
- Description: Update note title and content.
- Request body:
```json
{ "title": "Updated", "content": "Updated content" }
```
- Validation:
  - `title`: required, min length 1, max length 200
  - `content`: required, min length 1
- Responses:
  - `200 OK` with updated note payload
  - `404 Not Found` when note does not exist
  - `422 Unprocessable Entity` on validation failure

### `DELETE /notes/{note_id}`
- Description: Delete a note.
- Responses:
  - `204 No Content`
  - `404 Not Found` when note does not exist

## Action Items

### `GET /action-items/`
- Description: List all action items.
- Response: `200 OK`
- Body:
```json
[
  { "id": 1, "description": "Ship feature", "completed": false }
]
```

### `POST /action-items/`
- Description: Create an action item. `completed` defaults to `false`.
- Request body:
```json
{ "description": "Ship feature" }
```
- Validation:
  - `description`: required, min length 1
- Responses:
  - `201 Created`
  - Body:
```json
{ "id": 1, "description": "Ship feature", "completed": false }
```
  - `422 Unprocessable Entity` on validation failure

### `PUT /action-items/{item_id}/complete`
- Description: Mark an action item as completed.
- Responses:
  - `200 OK`
  - Body:
```json
{ "id": 1, "description": "Ship feature", "completed": true }
```
  - `404 Not Found` with `{ "detail": "Action item not found" }`
