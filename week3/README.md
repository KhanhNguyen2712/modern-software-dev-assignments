# Week 3 — Custom MCP Server (STDIO Transport)

## 📋 Tổng quan

MCP Server chạy trên **STDIO transport**, xây dựng bằng Python + [FastMCP](https://gofastmcp.com/) (thư viện chính thức).  
Server cung cấp **2 Tools**, **2 Resources**, **1 Prompt** — tích hợp với Claude Desktop hoặc bất kỳ MCP client nào.

---

## 🏗️ Cấu trúc thư mục

```
week3/
├── README.md                    ← Bạn đang đọc file này
├── .env.example                 ← Mẫu biến môi trường
└── server/
    ├── pyproject.toml           ← Dependencies
    ├── app/
    │   ├── stdio_main.py        ← 🚀 STDIO entry-point (file chính)
    │   ├── remote_main.py       ← HTTP entry-point (remote mode)
    │   └── main.py              ← FastAPI wrapper
    └── core/
        ├── __init__.py
        ├── client.py            ← Open-Meteo HTTP client
        ├── config.py            ← Settings & env parsing
        ├── errors.py            ← Custom exceptions
        ├── models.py            ← Pydantic data models
        └── service.py           ← Weather business logic
```

---

## ⚙️ Yêu cầu hệ thống

- **Python**: >= 3.11
- **Conda environment**: `week3-mcp`
- **Thư viện chính**: `fastmcp >= 3.0`, `httpx`, `pydantic`, `python-dotenv`

---

## 🚀 Cài đặt & Chạy server

### Bước 1: Kích hoạt môi trường conda

```bash
conda activate week3-mcp
```

### Bước 2: Cài đặt dependencies (nếu chưa cài)

```bash
pip install fastmcp httpx pydantic pydantic-settings python-dotenv
```

### Bước 3: Chạy server STDIO

```bash
cd week3/server
python app/stdio_main.py
```

> ⚠️ Khi chạy ở chế độ STDIO, server sẽ **lắng nghe trên stdin** và **trả kết quả trên stdout**.  
> Tất cả log được chuyển hướng sang **stderr** để không nhiễu luồng JSON-RPC.

---

## 🛠️ Tính năng đã triển khai

### Tools (02)

| Tên Tool | Mô tả | Tham số |
|---|---|---|
| `tool_nghien_cuu` | Nhận từ khóa, trả về dữ liệu nghiên cứu giả lập (JSON) | `keyword` (str, bắt buộc) |
| `tool_tinh_toan` | Thực hiện phép tính số học / logic | `operator` (str), `a` (float), `b` (float, tùy chọn) |

**Operators hỗ trợ:** `add`, `subtract`, `multiply`, `divide`, `power`, `sqrt`, `modulo`

### Resources (02)

| URI | Mô tả | MIME Type |
|---|---|---|
| `resource://config/settings` | Cấu hình hệ thống (JSON) | `application/json` |
| `resource://docs/readme` | Hướng dẫn sử dụng server | `text/plain` |

### Prompts (01)

| Tên Prompt | Mô tả | Tham số |
|---|---|---|
| `prompt_tro_ly_phan_tich` | Mẫu prompt hướng dẫn AI phân tích dữ liệu | `keyword` (str), `operator` (str, mặc định "add") |

---

## 🖥️ Hướng dẫn Demo với Claude Desktop

### Bước 1: Mở file cấu hình Claude Desktop

Mở file cấu hình MCP của Claude Desktop. Trên **Windows**, file này nằm tại:

```
%APPDATA%\Claude\claude_desktop_config.json
```

Cách mở nhanh:
1. Mở **Claude Desktop**
2. Click vào biểu tượng ☰ (menu) → **Settings** → **Developer** → **Edit Config**

### Bước 2: Thêm cấu hình MCP server

Dán nội dung sau vào file `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "weather-mcp-stdio": {
      "command": "C:\\Users\\kelve\\anaconda3\\envs\\week3-mcp\\python.exe",
      "args": [
        "app\\stdio_main.py"
      ],
      "cwd": "C:\\Users\\kelve\\Code\\New folder\\modern-software-dev-assignments\\week3\\server"
    }
  }
}
```

> **Lưu ý:** Nếu bạn đã có `mcpServers` khác, chỉ cần thêm `"weather-mcp-stdio": {...}` vào bên trong object `mcpServers` đã có.

### Bước 3: Khởi động lại Claude Desktop

- Tắt hoàn toàn Claude Desktop (đóng cả trong system tray)
- Mở lại Claude Desktop

### Bước 4: Kiểm tra kết nối

Khi mở Claude Desktop, bạn sẽ thấy biểu tượng 🔌 (plug) hoặc 🔨 (hammer) ở góc dưới cùng bên phải ô nhập tin nhắn. Click vào đó sẽ hiển thị danh sách các tool có sẵn:

- ✅ `tool_nghien_cuu`
- ✅ `tool_tinh_toan`

### Bước 5: Demo thử các tính năng

#### 🔍 Demo Tool Nghiên cứu
Gõ vào Claude Desktop:
```
Hãy dùng tool nghiên cứu để tìm kiếm thông tin về "machine learning"
```

**Kết quả mong đợi:** Claude sẽ gọi `tool_nghien_cuu` và trả về dữ liệu nghiên cứu giả lập bao gồm title, summary, key concepts, và số lượng sources.

#### 🧮 Demo Tool Tính toán
```
Hãy dùng tool tính toán để tính 15 chia cho 4
```

**Kết quả mong đợi:** Claude gọi `tool_tinh_toan(operator="divide", a=15, b=4)` → result = 3.75

#### 📊 Demo Prompt Phân tích (kết hợp cả 2 tools)
```
Hãy sử dụng prompt phân tích để nghiên cứu chủ đề "blockchain" và thực hiện phép tính liên quan
```

**Kết quả mong đợi:** Claude sử dụng `prompt_tro_ly_phan_tich` để tạo workflow phân tích, sau đó lần lượt gọi cả 2 tools để tổng hợp báo cáo hoàn chỉnh.

---

## 🔍 Kiểm tra nhanh bằng FastMCP CLI (thay thế MCP Inspector)

Nếu bạn muốn test nhanh mà không cần Claude Desktop:

```bash
conda activate week3-mcp
cd week3/server

# Inspect server — liệt kê tools, resources, prompts
fastmcp inspect app/stdio_main.py:mcp

# Chạy dev server với MCP Inspector UI
fastmcp dev app/stdio_main.py:mcp
```

Lệnh `fastmcp dev` sẽ mở **MCP Inspector** trong trình duyệt (thường là `http://localhost:6274`), cho phép bạn:
- Xem danh sách tools/resources/prompts
- Gọi thử từng tool với tham số tùy chỉnh
- Xem kết quả trả về dạng JSON

---

## 📐 Kiến trúc & Thiết kế

### Logging Strategy
```
┌───────────────────────────────────────────────┐
│              MCP Client (Claude)              │
│                                               │
│  stdin ──────────────→ JSON-RPC Request       │
│  stdout ←──────────── JSON-RPC Response       │
│                                               │
│  (stderr nhận toàn bộ log — không nhiễu)      │
└───────────────────────────────────────────────┘
```

### TextContent Output
Tất cả kết quả từ tools đều trả về dạng **chuỗi JSON** (string), được FastMCP tự động wrap thành `TextContent` theo chuẩn MCP specification.

### Error Handling
- Input validation (keyword rỗng, operator không hợp lệ)
- Division by zero protection
- Negative square root detection
- Graceful error messages dạng JSON

---

## 📝 Ví dụ Input / Output

### tool_nghien_cuu

**Input:**
```json
{ "keyword": "machine learning" }
```

**Output:**
```json
{
  "status": "success",
  "keyword": "machine learning",
  "data": {
    "title": "Introduction to Machine Learning",
    "summary": "Machine learning is a subset of AI ...",
    "key_concepts": ["supervised learning", "unsupervised learning", "reinforcement learning"],
    "sources": 42,
    "last_updated": "2025-12-01"
  },
  "retrieved_at": "2026-04-04T14:00:00+00:00"
}
```

### tool_tinh_toan

**Input:**
```json
{ "operator": "multiply", "a": 6, "b": 7 }
```

**Output:**
```json
{
  "status": "success",
  "expression": "multiply(6.0, 7.0)",
  "result": 42.0,
  "computed_at": "2026-04-04T14:00:00+00:00"
}
```
