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


def test_action_items_can_be_filtered_by_completed_state(client):
    first = client.post("/action-items/", json={"description": "Open"}).json()["data"]
    second = client.post("/action-items/", json={"description": "Done"}).json()["data"]
    client.put(f"/action-items/{second['id']}/complete")

    open_items = client.get("/action-items/", params={"completed": "false"}).json()["data"]["items"]
    done_items = client.get("/action-items/", params={"completed": "true"}).json()["data"]["items"]

    assert [item["id"] for item in open_items] == [first["id"]]
    assert [item["id"] for item in done_items] == [second["id"]]


def test_bulk_complete_marks_multiple_items_done(client):
    first = client.post("/action-items/", json={"description": "One"}).json()["data"]
    second = client.post("/action-items/", json={"description": "Two"}).json()["data"]

    response = client.post(
        "/action-items/bulk-complete",
        json={"ids": [first["id"], second["id"]]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert sorted(item["id"] for item in body["data"]["items"]) == [first["id"], second["id"]]
    assert all(item["completed"] is True for item in body["data"]["items"])


def test_bulk_complete_rolls_back_when_any_id_is_missing(client):
    first = client.post("/action-items/", json={"description": "One"}).json()["data"]
    second = client.post("/action-items/", json={"description": "Two"}).json()["data"]

    response = client.post("/action-items/bulk-complete", json={"ids": [first["id"], 999]})

    assert response.status_code == 404

    items = client.get("/action-items/").json()["data"]["items"]
    status_by_id = {item["id"]: item["completed"] for item in items}
    assert status_by_id[first["id"]] is False
    assert status_by_id[second["id"]] is False
