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


def test_update_note(client):
    # Create a note first
    payload = {"title": "Original Title", "content": "Original Content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Update the note
    update_payload = {"title": "Updated Title", "content": "Updated Content"}
    r = client.put(f"/notes/{note_id}", json=update_payload)
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated Content"

    # Verify the update persisted
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated Content"


def test_update_note_not_found(client):
    update_payload = {"title": "Updated Title", "content": "Updated Content"}
    r = client.put("/notes/99999", json=update_payload)
    assert r.status_code == 404


def test_partial_update_note(client):
    # Create a note first
    payload = {"title": "Original Title", "content": "Original Content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Partial update - only title
    update_payload = {"title": "Updated Title Only"}
    r = client.put(f"/notes/{note_id}", json=update_payload)
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Updated Title Only"
    assert data["content"] == "Original Content"


def test_delete_note(client):
    # Create a note first
    payload = {"title": "Note to Delete", "content": "This will be deleted"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Delete the note
    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    # Verify the note is gone
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_delete_note_not_found(client):
    r = client.delete("/notes/99999")
    assert r.status_code == 404
