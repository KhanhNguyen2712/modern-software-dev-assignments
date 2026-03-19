# Week 3 MCP Weather Server Plan

## Summary
- Xây một MCP server Python trong `week3/` bọc API thời tiết, dùng kiến trúc `shared core + 2 transports`.
- Transport 1: `STDIO` để đáp ứng chắc phần rubric local MCP.
- Transport 2: `HTTP` để lấy extra credit, dùng bearer-token validation ở lớp MCP server, không chuyển token sang upstream weather API.
- Upstream mặc định: `Open-Meteo` với 2 nhóm endpoint: geocoding để chuẩn hóa địa điểm và forecast/current weather để lấy dữ liệu.
- Mục tiêu chốt: đạt đủ `2+ tools`, có `resources` và `prompt` để bám learning goals, có resilience, docs đầy đủ, demo được cả local lẫn remote.

## Implementation Changes
- Tạo package `week3/server/` gồm 3 lớp:
  - `core`: config, typed schemas, Open-Meteo client, location resolver, error mapping, retry/timeout/rate-limit warning.
  - `mcp`: đăng ký tools/resources/prompts và format output theo MCP.
  - `transports`: entrypoint `stdio_main.py` và app `http_app.py`.
- Tool contract chốt:
  - `get_current_weather(location: str, units: Literal["metric","imperial"]="metric")`
  - `get_forecast(location: str, days: int=3, units: Literal["metric","imperial"]="metric")`
- Resource/prompt contract chốt:
  - Resource template `weather://current/{location}`
  - Resource template `weather://forecast/{location}?days={days}`
  - Prompt `weather_trip_brief` để model sinh tóm tắt/quyết định mang đồ theo dự báo
- Internal flow bắt buộc cho cả 2 tools:
  - Chuẩn hóa input location qua geocoding
  - Gọi forecast API bằng lat/lon đã resolve
  - Chuẩn hóa output thành text ngắn gọn + structured metadata
  - Map lỗi upstream sang lỗi người dùng hiểu được: invalid location, timeout, empty result, 429, 5xx
- Logging:
  - STDIO không ghi vào `stdout`; chỉ ghi `stderr` hoặc file logger
  - HTTP dùng request logging riêng, có request id cơ bản
- HTTP auth:
  - Chỉ bảo vệ transport HTTP, không áp vào STDIO
  - Verify bearer token bằng `issuer/JWKS` hoặc cấu hình dev token validator
  - Bắt buộc kiểm tra `aud` khớp server audience
  - Không forward bearer token sang Open-Meteo
  - Expose metadata endpoint cho protected resource discovery
- Docs/deliverables:
  - `week3/README.md` mô tả setup, env vars, run commands, Claude Desktop config cho STDIO, cách gọi remote HTTP, tool reference, sample prompts/invocation flow
  - Source code và test đều nằm dưới `week3/`

## Public Interfaces And Defaults
- Run commands mặc định:
  - Local STDIO: `python -m week3.server.transports.stdio_main`
  - Remote HTTP: `uvicorn week3.server.transports.http_app:app --host 0.0.0.0 --port 8000`
- Env vars chốt:
  - `WEATHER_BASE_URL`, `WEATHER_TIMEOUT_SECONDS`, `WEATHER_USER_AGENT`
  - `MCP_LOG_LEVEL`
  - `MCP_AUTH_ISSUER`, `MCP_AUTH_AUDIENCE`, `MCP_AUTH_JWKS_URL`
  - `MCP_AUTH_REQUIRED=true` chỉ áp cho HTTP
- Không thêm database, cache bền vững, hay background jobs trong scope tuần 3.

## 4 Workstreams For 4 People
- Người 1, Core API + schemas:
  - Chịu trách nhiệm `core`
  - Hoàn thành config, Pydantic models, Open-Meteo client, geocoding + forecast service, timeout/retry/error mapping
  - Bàn giao contract Python ổn định cho Người 2 và 3
- Người 2, MCP STDIO:
  - Chịu trách nhiệm layer `mcp` + `stdio_main.py`
  - Đăng ký 2 tools, 2 resources, 1 prompt; format output; bảo đảm STDIO logging đúng chuẩn
  - Demo được với MCP Inspector hoặc Claude Desktop local
- Người 3, Remote HTTP + auth:
  - Chịu trách nhiệm `http_app.py` và auth middleware/validator
  - Expose HTTP MCP transport, bearer validation, audience check, metadata endpoint, remote smoke test
  - Không được thay đổi contract tool nếu chưa đồng bộ với Người 2
- Người 4, Test + docs + integration:
  - Chịu trách nhiệm `week3/tests/` và `week3/README.md`
  - Viết test unit/integration/e2e, chuẩn bị cấu hình Claude Desktop mẫu, ví dụ remote call, acceptance checklist theo rubric
  - Chốt demo script và rà soát DX trước nộp bài

## Test Plan
- Unit tests:
  - resolve location thành công/thất bại
  - current weather và forecast parse đúng
  - timeout, empty result, 429, 5xx được map đúng lỗi
  - units và `days` validation đúng
- MCP integration tests:
  - server đăng ký đúng 2 tools, 2 resources, 1 prompt
  - tool trả output có nghĩa với location hợp lệ
  - location không hợp lệ trả lỗi graceful
- HTTP/auth tests:
  - request không token bị từ chối
  - token sai issuer/audience bị từ chối
  - token hợp lệ gọi tool thành công
  - metadata endpoint trả đúng thông tin protected resource
- Manual acceptance:
  - Claude Desktop/Cursor gọi được STDIO server
  - remote endpoint gọi được qua MCP-aware client hoặc proxy
  - README đủ để một người khác setup và chạy lại mà không hỏi thêm

## Assumptions
- Chọn `Open-Meteo` vì không cần auth upstream, giúp tách biệt rõ extra-credit auth ở MCP server.
- “OAuth2/Bearer” trong scope này nghĩa là resource server xác thực bearer token và công bố metadata; không xây full authorization server riêng.
- Trình tự thực hiện: hoàn tất core + STDIO trước, sau đó mở HTTP/auth, cuối cùng mới khóa docs và demo.
- Nếu thời gian thiếu, vẫn phải giữ đủ `STDIO + 2 tools + resilience + README`; HTTP/auth là phần mở rộng sau cùng nhưng đã được thiết kế để ghép vào mà không đổi contract.
