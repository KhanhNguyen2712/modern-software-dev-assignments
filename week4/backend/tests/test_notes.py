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


def test_search_notes_case_insensitive(client):
    client.post("/notes/", json={"title": "Deploy Plan", "content": "Ship release this Friday"})

    r = client.get("/notes/search/", params={"q": "deploy"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["title"] == "Deploy Plan"


def test_update_note(client):
    created = client.post("/notes/", json={"title": "Draft", "content": "Need edits"}).json()

    r = client.put(
        f"/notes/{created['id']}",
        json={"title": "Final", "content": "Ready to publish"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Final"
    assert data["content"] == "Ready to publish"


def test_delete_note(client):
    created = client.post("/notes/", json={"title": "Remove", "content": "To be deleted"}).json()

    r = client.delete(f"/notes/{created['id']}")
    assert r.status_code == 204

    r = client.get(f"/notes/{created['id']}")
    assert r.status_code == 404


def test_create_note_validation(client):
    r = client.post("/notes/", json={"title": "", "content": "body"})
    assert r.status_code == 422

    r = client.post("/notes/", json={"title": "valid", "content": ""})
    assert r.status_code == 422
