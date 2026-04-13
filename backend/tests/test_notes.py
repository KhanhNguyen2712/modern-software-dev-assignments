def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_delete_all_notes():
    # 1. Thêm một note nháp trước để đảm bảo có dữ liệu
    client.post("/notes/", json={"title": "Test Note", "content": "To be deleted"})
    
    # 2. Gọi API xóa tất cả
    response = client.delete("/notes/")
    assert response.status_code == 204 # 204 No Content là chuẩn cho DELETE
    
    # 3. Lấy lại danh sách notes xem đã rỗng chưa
    get_response = client.get("/notes/")
    assert get_response.status_code == 200
    assert len(get_response.json()) == 0