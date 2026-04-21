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
    assert body["data"]["total"] == 1
    assert body["data"]["page"] == 1
    assert body["data"]["page_size"] == 10
    assert len(body["data"]["items"]) == 1


def test_missing_action_item_returns_not_found_envelope(client):
    response = client.put("/action-items/999/complete")

    assert response.status_code == 404
    assert response.json() == {
        "ok": False,
        "error": {"code": "NOT_FOUND", "message": "Action item not found"},
    }


def test_action_items_list_supports_pagination_boundaries(client):
    for index in range(3):
        client.post("/action-items/", json={"description": f"Task {index}"})

    response = client.get("/action-items/", params={"page": 2, "page_size": 2})

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["total"] == 3
    assert body["data"]["page"] == 2
    assert body["data"]["page_size"] == 2
    assert len(body["data"]["items"]) == 1

    empty_page = client.get("/action-items/", params={"page": 3, "page_size": 2})
    assert empty_page.status_code == 200
    assert empty_page.json()["data"]["items"] == []


def test_action_items_list_rejects_too_large_page_size(client):
    response = client.get("/action-items/", params={"page_size": 500})

    assert response.status_code == 400
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
