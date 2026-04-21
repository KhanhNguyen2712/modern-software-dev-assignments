def test_create_and_complete_action_item_use_success_envelopes(client):
    payload = {"description": "Ship it"}
    response = client.post("/action-items/", json=payload)

    assert response.status_code == 201, response.text
    item = response.json()["data"]
    assert item["completed"] is False

    response = client.put(f"/action-items/{item['id']}/complete")

    assert response.status_code == 200
    done = response.json()
    assert done["ok"] is True
    assert done["data"]["completed"] is True

    response = client.get("/action-items/")

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert len(body["data"]) == 1


def test_missing_action_item_returns_not_found_envelope(client):
    response = client.put("/action-items/999/complete")

    assert response.status_code == 404
    assert response.json() == {
        "ok": False,
        "error": {"code": "NOT_FOUND", "message": "Action item not found"},
    }
