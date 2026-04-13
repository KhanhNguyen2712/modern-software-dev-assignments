# Hướng dẫn tương tác với Codebase (CS146s)

## Cấu trúc dự án
- **Backend**: FastAPI nằm ở `backend/app/`. Các API routes nằm trong `backend/app/routers/`.
- **Database**: SQLite. Schema nằm ở `backend/app/schemas.py` và models ở `backend/app/models.py`. Dữ liệu mẫu ở `data/seed.sql`.
- **Frontend**: Frontend thuần tĩnh (Vanilla JS/HTML/CSS) ở `frontend/`. Không dùng Node.js/React.
- **Tài liệu**: Các task cần làm nằm trong `docs/TASKS.md`.

## Quy trình làm việc bắt buộc (Vibe Coding Rules)
1. **Trước khi code tính năng mới**: Hãy kiểm tra `docs/TASKS.md` để hiểu bối cảnh.
2. **Khi thêm API Route mới**: 
   - Phải thêm test case tương ứng vào `backend/tests/`.
   - Update file `frontend/app.js` nếu API đó cần hiển thị lên UI.
3. **Guardrails (An toàn)**:
   - TUYỆT ĐỐI KHÔNG sửa các cấu hình trong `pre-commit-config.yaml` hay `Makefile` nếu không có lệnh rõ ràng.
   - Luôn sử dụng lệnh `make format` và `make lint` sau khi sửa code Python.