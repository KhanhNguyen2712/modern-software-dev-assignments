def test_create_list_attach_detach_and_filter_tags(client):
    note = client.post("/notes/", json={"title": "Tagged", "content": "Content"}).json()["data"]

    create_tag = client.post("/tags/", json={"name": "urgent"})
    assert create_tag.status_code == 201
    tag = create_tag.json()["data"]

    list_tags = client.get("/tags/")
    assert list_tags.status_code == 200
    assert [item["name"] for item in list_tags.json()["data"]] == ["urgent"]

    attach = client.post(f"/notes/{note['id']}/tags", json={"tag_id": tag["id"]})
    assert attach.status_code == 200
    attached_note = attach.json()["data"]
    assert [item["name"] for item in attached_note["tags"]] == ["urgent"]

    filtered_notes = client.get("/notes/", params={"tag_id": tag["id"]})
    assert filtered_notes.status_code == 200
    filtered_items = filtered_notes.json()["data"]["items"]
    assert [item["id"] for item in filtered_items] == [note["id"]]

    detach = client.delete(f"/notes/{note['id']}/tags/{tag['id']}")
    assert detach.status_code == 200
    assert detach.json()["data"]["detached"] is True

    after_detach = client.get("/notes/", params={"tag_id": tag["id"]})
    assert after_detach.status_code == 200
    assert after_detach.json()["data"]["items"] == []


def test_missing_tag_or_note_returns_not_found(client):
    note = client.post("/notes/", json={"title": "Tagged", "content": "Content"}).json()["data"]

    attach_missing_tag = client.post(f"/notes/{note['id']}/tags", json={"tag_id": 999})
    attach_missing_note = client.post("/notes/999/tags", json={"tag_id": 999})
    delete_missing_tag = client.delete("/tags/999")

    assert attach_missing_tag.status_code == 404
    assert attach_missing_note.status_code == 404
    assert delete_missing_tag.status_code == 404
