from backend.app.services.extract import extract_action_items, extract_tags


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "Ship it!" in items


def test_extract_tags():
    text = "Plan #Launch and #QA before release."

    tags = extract_tags(text)

    assert tags == ["launch", "qa"]


def test_extract_endpoint_returns_structured_results_and_can_apply(client):
    note = client.post(
        "/notes/",
        json={
            "title": "Extract me",
            "content": "Plan #Launch\n- [ ] Write tests\n- [ ] Ship release",
        },
    ).json()["data"]

    preview = client.post(f"/notes/{note['id']}/extract")
    assert preview.status_code == 200
    preview_body = preview.json()["data"]
    assert preview_body["applied"] is False
    assert preview_body["tags"] == ["launch"]
    assert preview_body["action_items"] == ["Write tests", "Ship release"]

    applied = client.post(f"/notes/{note['id']}/extract", params={"apply": "true"})
    assert applied.status_code == 200
    applied_body = applied.json()["data"]
    assert applied_body["applied"] is True

    note_after = client.get(f"/notes/{note['id']}").json()["data"]
    assert [tag["name"] for tag in note_after["tags"]] == ["launch"]

    action_items = client.get("/action-items/").json()["data"]["items"]
    descriptions = [item["description"] for item in action_items]
    assert descriptions == ["Write tests", "Ship release"]
