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
    assert len(body["data"]) >= 1


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
