# API Documentation

## Overview

Base URL: `http://localhost:8000`

All endpoints return JSON. Error responses follow the standard FastAPI format with a `detail` field.

---

## Notes API

Base path: `/notes`

### 1. List All Notes

Returns a list of all notes in the system.

- **Method:** `GET`
- **Path:** `/notes/`
- **Description:** Retrieve all notes from the database
- **Request Body:** None
- **Response Example:**
  ```json
  [
    {
      "id": 1,
      "title": "Meeting Notes",
      "content": "Discussed project timeline"
    },
    {
      "id": 2,
      "title": "Shopping List",
      "content": "Buy milk and eggs"
    }
  ]
  ```
- **Status Codes:**
  - `200 OK` - Successfully retrieved notes

---

### 2. Create Note

Creates a new note with the provided title and content.

- **Method:** `POST`
- **Path:** `/notes/`
- **Description:** Create a new note
- **Request Body:**
  ```json
  {
    "title": "string (required)",
    "content": "string (required)"
  }
  ```
- **Response Example:**
  ```json
  {
    "id": 1,
    "title": "Meeting Notes",
    "content": "Discussed project timeline"
  }
  ```
- **Status Codes:**
  - `201 Created` - Note created successfully
  - `422 Unprocessable Entity` - Validation error (missing/invalid fields)

---

### 3. Search Notes

Searches notes by title or content. Returns all notes if no query parameter is provided.

- **Method:** `GET`
- **Path:** `/notes/search/`
- **Description:** Search notes by title or content (case-insensitive partial match)
- **Query Parameters:**
  - `q` (optional): Search query string
- **Request Body:** None
- **Response Example:**
  ```json
  [
    {
      "id": 1,
      "title": "Meeting Notes",
      "content": "Discussed project timeline"
    }
  ]
  ```
- **Status Codes:**
  - `200 OK` - Successfully retrieved search results

---

### 4. Get Note by ID

Retrieves a specific note by its ID.

- **Method:** `GET`
- **Path:** `/notes/{note_id}`
- **Description:** Retrieve a single note by ID
- **Path Parameters:**
  - `note_id` (int, required): The ID of the note to retrieve
- **Request Body:** None
- **Response Example:**
  ```json
  {
    "id": 1,
    "title": "Meeting Notes",
    "content": "Discussed project timeline"
  }
  ```
- **Status Codes:**
  - `200 OK` - Note found and returned
  - `404 Not Found` - Note with given ID does not exist

---

### 5. Delete Note

Deletes a note by its ID.

- **Method:** `DELETE`
- **Path:** `/notes/{note_id}`
- **Description:** Delete a note by ID
- **Path Parameters:**
  - `note_id` (int, required): The ID of the note to delete
- **Request Body:** None
- **Response Example:**
  ```json
  {
    "message": "Note deleted successfully"
  }
  ```
- **Status Codes:**
  - `200 OK` - Note deleted successfully
  - `404 Not Found` - Note with given ID does not exist

---

### 6. Update Note

Updates the title and content of an existing note.

- **Method:** `PUT`
- **Path:** `/notes/{note_id}`
- **Description:** Update an existing note's title and content
- **Path Parameters:**
  - `note_id` (int, required): The ID of the note to update
- **Request Body:**
  ```json
  {
    "title": "string (required)",
    "content": "string (required)"
  }
  ```
- **Response Example:**
  ```json
  {
    "id": 1,
    "title": "Updated Title",
    "content": "Updated content"
  }
  ```
- **Status Codes:**
  - `200 OK` - Note updated successfully
  - `404 Not Found` - Note with given ID does not exist
  - `422 Unprocessable Entity` - Validation error (missing/invalid fields)

---

## Action Items API

Base path: `/action-items`

### 1. List All Action Items

Returns a list of all action items in the system.

- **Method:** `GET`
- **Path:** `/action-items/`
- **Description:** Retrieve all action items from the database
- **Request Body:** None
- **Response Example:**
  ```json
  [
    {
      "id": 1,
      "description": "Call the supplier",
      "completed": false
    },
    {
      "id": 2,
      "description": "Send weekly report",
      "completed": true
    }
  ]
  ```
- **Status Codes:**
  - `200 OK` - Successfully retrieved action items

---

### 2. Create Action Item

Creates a new action item with the provided description. Created with `completed` status set to `false`.

- **Method:** `POST`
- **Path:** `/action-items/`
- **Description:** Create a new action item (defaults to incomplete)
- **Request Body:**
  ```json
  {
    "description": "string (required)"
  }
  ```
- **Response Example:**
  ```json
  {
    "id": 1,
    "description": "Call the supplier",
    "completed": false
  }
  ```
- **Status Codes:**
  - `201 Created` - Action item created successfully
  - `422 Unprocessable Entity` - Validation error (missing/invalid fields)

---

### 3. Complete Action Item

Marks an action item as completed.

- **Method:** `PUT`
- **Path:** `/action-items/{item_id}/complete`
- **Description:** Mark an action item as completed
- **Path Parameters:**
  - `item_id` (int, required): The ID of the action item to complete
- **Request Body:** None
- **Response Example:**
  ```json
  {
    "id": 1,
    "description": "Call the supplier",
    "completed": true
  }
  ```
- **Status Codes:**
  - `200 OK` - Action item marked as completed
  - `404 Not Found` - Action item with given ID does not exist

---

## Schemas

### NoteCreate
```json
{
  "title": "string (max 200 chars)",
  "content": "string"
}
```

### NoteRead
```json
{
  "id": "integer",
  "title": "string",
  "content": "string"
}
```

### NoteUpdate
```json
{
  "title": "string",
  "content": "string"
}
```

### ActionItemCreate
```json
{
  "description": "string"
}
```

### ActionItemRead
```json
{
  "id": "integer",
  "description": "string",
  "completed": "boolean"
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `404 Not Found` - Resource does not exist
- `422 Unprocessable Entity` - Validation error (e.g., missing required fields, invalid data types)
- `405 Method Not Allowed` - HTTP method not supported for this endpoint
- `500 Internal Server Error` - Server-side error

---

## Interactive Documentation

FastAPI provides interactive API documentation that can be accessed when the server is running:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
