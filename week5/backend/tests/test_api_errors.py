def test_notes_related_endpoints_return_expected_400_and_404(client):
    note = client.post("/notes/", json={"title": "Alpha", "content": "Body #tag"}).json()["data"]
    tag = client.post("/tags/", json={"name": "tag"}).json()["data"]

    invalid_search = client.get("/notes/search", params={"sort": "wrong"})
    invalid_update = client.put(f"/notes/{note['id']}", json={"title": "", "content": ""})
    missing_note = client.get("/notes/999")
    missing_extract = client.post("/notes/999/extract")
    missing_attach = client.post(f"/notes/{note['id']}/tags", json={"tag_id": 999})
    missing_detach = client.delete(f"/notes/{note['id']}/tags/999")

    assert invalid_search.status_code == 400
    assert invalid_update.status_code == 400
    assert missing_note.status_code == 404
    assert missing_extract.status_code == 404
    assert missing_attach.status_code == 404
    assert missing_detach.status_code == 404
    assert tag["name"] == "tag"


def test_action_item_endpoints_return_expected_400_and_404(client):
    invalid_create = client.post("/action-items/", json={"description": ""})
    missing_complete = client.put("/action-items/999/complete")
    bulk_missing = client.post("/action-items/bulk-complete", json={"ids": [999]})

    assert invalid_create.status_code == 400
    assert missing_complete.status_code == 404
    assert bulk_missing.status_code == 404


def test_tag_endpoints_return_expected_400_and_404(client):
    first = client.post("/tags/", json={"name": "launch"})
    duplicate = client.post("/tags/", json={"name": "launch"})
    invalid = client.post("/tags/", json={"name": ""})
    missing = client.delete("/tags/999")

    assert first.status_code == 201
    assert duplicate.status_code == 400
    assert invalid.status_code == 400
    assert missing.status_code == 404


def test_bulk_complete_is_stable_across_repeated_requests(client):
    first = client.post("/action-items/", json={"description": "One"}).json()["data"]
    second = client.post("/action-items/", json={"description": "Two"}).json()["data"]

    first_pass = client.post("/action-items/bulk-complete", json={"ids": [first["id"], second["id"]]})
    second_pass = client.post("/action-items/bulk-complete", json={"ids": [first["id"], second["id"]]})

    assert first_pass.status_code == 200
    assert second_pass.status_code == 200
    assert all(item["completed"] is True for item in second_pass.json()["data"]["items"])
