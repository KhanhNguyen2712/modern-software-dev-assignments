Chạy test suite cho week4 backend.

Steps:
1. Chạy: `pytest -q backend/tests --maxfail=1 -x`
2. Nếu pass: `pytest --cov=backend/app backend/tests`
3. Tóm tắt: pass/fail count, coverage %, gợi ý fix nếu lỗi.

Arguments: $ARGUMENTS