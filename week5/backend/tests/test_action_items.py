def test_create_and_complete_action_item(client):
    response = client.post("/action-items/", json={"description": "Ship it"})
    assert response.status_code == 201, response.text
    item = response.json()
    assert item["completed"] is False

    response = client.put(f"/action-items/{item['id']}/complete")
    assert response.status_code == 200
    done = response.json()
    assert done["completed"] is True

    response = client.get("/action-items/")
    assert response.status_code == 200
    payload = response.json()
    items = payload["items"]
    assert payload["total"] == 1
    assert len(items) == 1


def test_action_item_filters(client):
    open_item = client.post("/action-items/", json={"description": "Open task"}).json()
    done_item = client.post("/action-items/", json={"description": "Done task"}).json()
    assert client.put(f"/action-items/{done_item['id']}/complete").status_code == 200

    response = client.get("/action-items/", params={"completed": "false"})
    assert response.status_code == 200
    assert [item["id"] for item in response.json()["items"]] == [open_item["id"]]

    response = client.get("/action-items/", params={"completed": "true"})
    assert response.status_code == 200
    assert [item["id"] for item in response.json()["items"]] == [done_item["id"]]


def test_bulk_complete_marks_all_requested_items(client):
    first = client.post("/action-items/", json={"description": "First"}).json()
    second = client.post("/action-items/", json={"description": "Second"}).json()

    response = client.post(
        "/action-items/bulk-complete",
        json={"ids": [second["id"], first["id"]]},
    )
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["count"] == 2
    assert [item["id"] for item in data["items"]] == [second["id"], first["id"]]
    assert all(item["completed"] is True for item in data["items"])


def test_bulk_complete_rolls_back_when_any_id_is_missing(client):
    first = client.post("/action-items/", json={"description": "First"}).json()
    second = client.post("/action-items/", json={"description": "Second"}).json()

    response = client.post("/action-items/bulk-complete", json={"ids": [first["id"], 9999]})
    assert response.status_code == 404
    assert "9999" in response.json()["detail"]

    response = client.get("/action-items/")
    assert response.status_code == 200
    items = {item["id"]: item for item in response.json()["items"]}
    assert items[first["id"]]["completed"] is False
    assert items[second["id"]]["completed"] is False


def test_action_item_validation_errors(client):
    response = client.post("/action-items/", json={"description": "   "})
    assert response.status_code == 422

    response = client.post("/action-items/bulk-complete", json={"ids": []})
    assert response.status_code == 422
