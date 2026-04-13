# Test, Analyze & Fix

Run the week4 test suite, analyze results, and help fix any failures.

## Instructions

1. Run the test suite:
   ```
   PYTHONPATH=. pytest -q backend/tests --maxfail=3 -x --tb=short $ARGUMENTS
   ```

2. If ALL tests PASS:
   - Run coverage: `PYTHONPATH=. pytest --cov=backend/app backend/tests --cov-report=term-missing`
   - Summarize which files and lines lack test coverage
   - Suggest 2-3 specific test cases that would improve coverage
   - End with a ✅ summary

3. If any tests FAIL:
   - For each failing test, show:
     a. The test name and assertion error
     b. The relevant source code that's likely buggy
     c. A proposed fix (show the exact diff)
   - Ask me if I want to apply the fixes
   - After applying, re-run the test suite to confirm everything passes

4. After all tests pass, run the formatter:
   ```
   make format
   ```

5. Print a final summary table:
   | Metric | Value |
   |--------|-------|
   | Tests run | N |
   | Tests passed | N |
   | Tests failed | N |
   | Coverage | X% |
