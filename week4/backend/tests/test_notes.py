def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_delete_note_success(client):
    # Create a note first
    payload = {"title": "To Delete", "content": "Delete me"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Delete the note
    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 200
    assert r.json()["message"] == "Note deleted successfully"

    # Verify the note is gone
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_delete_note_not_found(client):
    # Try to delete a non-existent note
    r = client.delete("/notes/99999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Note not found"


def test_update_note_success(client):
    # Create a note first
    payload = {"title": "Original Title", "content": "Original content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Update the note
    update_payload = {"title": "Updated Title", "content": "Updated content"}
    r = client.put(f"/notes/{note_id}", json=update_payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content"
    assert data["id"] == note_id

    # Verify the note is actually updated
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content"


def test_update_note_not_found(client):
    # Try to update a non-existent note
    update_payload = {"title": "Updated Title", "content": "Updated content"}
    r = client.put("/notes/99999", json=update_payload)
    assert r.status_code == 404
    assert r.json()["detail"] == "Note not found"
