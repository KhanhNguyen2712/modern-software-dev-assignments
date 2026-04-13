# Mô tả:
Chạy toàn bộ quy trình kiểm tra chất lượng code (Format, Lint, Test) trước khi commit.

# Đầu vào:
Không yêu cầu đầu vào.

# Hành động:
1. Chạy lệnh `black .` để tự động format code bằng black.
2. Chạy lệnh `ruff check .` để kiểm tra lỗi bằng ruff.
3. Chạy lệnh `pytest` để chạy toàn bộ pytest trong thư mục `backend/tests/`.

# Đầu ra:
- Nếu tất cả đều xanh (Pass): In ra thông báo "✅ Mọi thứ hoàn hảo! Code đã sẵn sàng để commit." và liệt kê tóm tắt các test đã pass.
- Nếu có lỗi (Fail): Dừng lại ngay lập tức, tóm tắt lỗi nằm ở file nào, dòng nào và đề xuất cách sửa (fix) cho tôi. Đừng tự động sửa trừ khi tôi cho phép.