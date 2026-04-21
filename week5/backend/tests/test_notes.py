def test_create_and_list_notes_use_success_envelopes(client):
    payload = {"title": "Test", "content": "Hello world"}
    response = client.post("/notes/", json=payload)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["ok"] is True
    assert body["data"]["title"] == "Test"

    response = client.get("/notes/")

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["data"]["total"] >= 1
    assert body["data"]["page"] == 1
    assert body["data"]["page_size"] == 10
    assert len(body["data"]["items"]) >= 1


def test_missing_note_returns_not_found_envelope(client):
    response = client.get("/notes/999")

    assert response.status_code == 404
    body = response.json()
    assert body == {
        "ok": False,
        "error": {"code": "NOT_FOUND", "message": "Note not found"},
    }


def test_invalid_note_payload_returns_validation_envelope(client):
    response = client.post("/notes/", json={"title": "", "content": ""})

    assert response.status_code == 400
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "title" in body["error"]["message"]


def test_notes_list_supports_pagination_boundaries(client):
    for index in range(3):
        client.post("/notes/", json={"title": f"Note {index}", "content": f"Body {index}"})

    response = client.get("/notes/", params={"page": 2, "page_size": 2})

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["total"] == 3
    assert body["data"]["page"] == 2
    assert body["data"]["page_size"] == 2
    assert len(body["data"]["items"]) == 1

    empty_page = client.get("/notes/", params={"page": 3, "page_size": 2})
    assert empty_page.status_code == 200
    assert empty_page.json()["data"]["items"] == []


def test_notes_list_rejects_too_large_page_size(client):
    response = client.get("/notes/", params={"page_size": 500})

    assert response.status_code == 400
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
