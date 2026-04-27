def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    response = client.post("/notes/", json=payload)
    assert response.status_code == 201, response.text

    data = response.json()
    assert data["title"] == "Test"
    assert "created_at" in data
    assert "updated_at" in data

    response = client.get("/notes/")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1


def test_search_notes_supports_case_insensitive_filters_pagination_and_sort(client):
    notes = [
        {"title": "zeta rollout", "content": "misc"},
        {"title": "Alpha spec", "content": "first project"},
        {"title": "bravo", "content": "contains alpha keyword"},
        {"title": "charlie", "content": "plain text"},
    ]
    for payload in notes:
        assert client.post("/notes/", json=payload).status_code == 201

    response = client.get(
        "/notes/search",
        params={"q": "ALPHA", "page": 1, "page_size": 1, "sort": "title_asc"},
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["page_size"] == 1
    assert [item["title"] for item in data["items"]] == ["Alpha spec"]

    response = client.get(
        "/notes/search",
        params={"q": "alpha", "page": 2, "page_size": 1, "sort": "title_asc"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert [item["title"] for item in data["items"]] == ["bravo"]


def test_search_notes_rejects_unsupported_sort(client):
    response = client.get("/notes/search", params={"sort": "priority_desc"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported sort value"


def test_update_and_delete_note(client):
    create_response = client.post("/notes/", json={"title": "Draft", "content": "Needs work"})
    note = create_response.json()

    update_response = client.put(
        f"/notes/{note['id']}",
        json={"title": "Final", "content": "Ready to ship"},
    )
    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated["title"] == "Final"
    assert updated["content"] == "Ready to ship"

    delete_response = client.delete(f"/notes/{note['id']}")
    assert delete_response.status_code == 204
    assert delete_response.text == ""

    get_response = client.get(f"/notes/{note['id']}")
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Note not found"


def test_note_validation_errors(client):
    response = client.post("/notes/", json={"title": "   ", "content": "valid"})
    assert response.status_code == 422

    response = client.put("/notes/999", json={"title": "Test", "content": "Still valid"})
    assert response.status_code == 404
