# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **Phan Gia Huy** \
SUNet ID: \
Citations: Anthropic Claude Code Best Practices (https://www.anthropic.com/engineering/claude-code-best-practices)

This assignment took me about **4** hours to do. 


## YOUR RESPONSES

### Automation #1: CLAUDE.md (Guidance File)

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Lấy cảm hứng từ tài liệu "Claude Code best practices", cụ thể là phần sử dụng file `CLAUDE.md` để cung cấp repository context và thiết lập các "safety guardrails". Việc này giúp định hình hành vi của AI ngay từ đầu, tránh việc nó sinh ra code lệch chuẩn.

b. Design of each automation, including goals, inputs/outputs, steps
> - **Goals:** Hướng dẫn Claude hiểu rõ cấu trúc dự án (FastAPI cho backend, Vanilla JS cho frontend, SQLite). Ép buộc quy tắc: thêm route mới phải kèm test, và không được tự ý sửa cấu hình dự án (Makefile, pre-commit).
> - **Inputs/Outputs:** Input là file tĩnh `CLAUDE.md` được Claude tự động đọc khi khởi động. Output là cách hành xử của Claude tuân thủ đúng luật lệ đã đề ra.
> - **Steps:** Claude đọc file -> Ghi nhớ bối cảnh -> Áp dụng các rules vào các prompt tiếp theo của người dùng.

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> - **How to run:** Tự động chạy khi khởi động lệnh `claude` trong thư mục gốc. Không cần gõ thêm lệnh.
> - **Expected outputs:** Claude xác nhận đã đọc hướng dẫn và bắt đầu trả lời/code dựa trên context đó.
> - **Rollback/safety:** Rất an toàn. Nếu muốn rollback, chỉ cần xóa hoặc đổi tên file `CLAUDE.md`.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> - **Before:** Khi yêu cầu code frontend, Claude thường tự động đề xuất dùng React hoặc Node.js (ảo giác framework). Thường xuyên quên viết test khi tạo API mới.
> - **After:** Nhờ `CLAUDE.md`, Claude tự động biết dùng Vanilla JS, biết tìm đến đúng file `backend/tests/` để viết test case mà không cần tôi phải nhắc lại trong từng prompt.

e. How you used the automation to enhance the starter application
> Tôi dùng nó để xây dựng tính năng "Delete All Notes". Nhờ automation này, khi tôi ra lệnh "thêm tính năng xóa tất cả ghi chú", Claude đã tự động nhảy vào `backend/app/routers/notes.py` để viết API, tự cập nhật UI bằng Vanilla JS trong `frontend/app.js`, và tự động sinh test case trong `test_notes.py` đúng như luật đã định.


### Automation #2: Slash command `/shipit` (Quality Assurance)

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Lấy cảm hứng từ phần "Custom slash commands" trong tài liệu best practices, đặc biệt là ví dụ về "Test runner with coverage". Tôi muốn tạo ra một workflow duy nhất để đảm bảo chất lượng code trước khi commit.

b. Design of each automation, including goals, inputs/outputs, steps
> - **Goals:** Tự động hóa quá trình chạy format code, linter và unit tests để giảm thiểu thao tác thủ công.
> - **Inputs/Outputs:** Không yêu cầu tham số đầu vào. Output là thông báo Pass (sẵn sàng commit) hoặc Fail (đi kèm tóm tắt lỗi và đề xuất cách sửa).
> - **Steps:** 1. Chạy `black .` (black & ruff --fix). 2. Chạy `ruff check .` (ruff). 3. Chạy `pytest`.

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> - **How to run:** Gõ `/shipit` trong giao diện dòng lệnh của Claude Code.
> - **Expected outputs:** Nếu pass, in ra "Mọi thứ hoàn hảo! Code đã sẵn sàng để commit." Nếu fail, dừng script và hiển thị traceback được tóm tắt.
> - **Rollback/safety:** Automation này rất an toàn vì nó chủ yếu gọi các lệnh kiểm tra read-only (`pytest`, `lint`) và bộ format tiêu chuẩn (`black`). Không can thiệp vào logic nghiệp vụ của app.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> - **Before:** Sau khi viết code, tôi phải tự gõ thủ công 3 lệnh: `black .`, `ruff check .`, `pytest`. Nếu có lỗi linter hoặc test fail, tôi phải lướt terminal đọc log rất dài để tự tìm ra nguyên nhân và sửa.
> - **After:** Chỉ cần gõ một lệnh `/shipit`. Nếu có lỗi, Claude sẽ tự đọc log, chỉ ra chính xác dòng code gây lỗi và đề xuất hướng fix trực tiếp trong cửa sổ chat, tiết kiệm rất nhiều thời gian debug.

e. How you used the automation to enhance the starter application
> Sau khi Claude hoàn thành việc sinh code cho tính năng "Delete All Notes", tôi đã gọi lệnh `/shipit`. Automation đã tự động format lại code Python cho chuẩn PEP8, kiểm tra các lỗi cú pháp tiềm ẩn và chạy cái test case `test_delete_all_notes()` mà chúng tôi vừa thêm vào. Nhờ `/shipit`, tôi tự tin rằng tính năng mới hoạt động hoàn hảo và không làm vỡ các routes cũ trước khi push code.