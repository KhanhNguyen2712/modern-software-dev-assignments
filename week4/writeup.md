# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: Claude Code best practices (https://www.anthropic.com/engineering/claude-code-best-practices), SubAgents overview (https://docs.anthropic.com/en/docs/claude-code/sub-agents)

This assignment took me about 24 hours to do. 


## YOUR RESPONSES
### Automation #1 — `CLAUDE.md` Repository Guidance File
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the [Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices) guide, specifically the section on using `CLAUDE.md` files to provide repository-specific context. The best practices doc recommends using `CLAUDE.md` to document project structure, coding conventions, safe/unsafe commands, and workflow patterns so that Claude can operate more autonomously and consistently within the codebase. I also drew from the idea of "guardrails" — telling Claude what it should and should not do — to prevent destructive actions like running `pip install` or `git push` without confirmation.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal:** Provide Claude Code with comprehensive, always-available context about the week4 project so it can navigate the codebase, follow coding conventions, and execute workflows correctly without repeated manual instructions.
>
> **Inputs:** None — `CLAUDE.md` is automatically loaded when Claude Code starts a session in the `week4/` directory.
>
> **Outputs:** Claude's behavior is guided by the file's contents. It will:
> - Know the full project structure (backend, frontend, data, docs)
> - Follow coding conventions (Pydantic schemas, SQLAlchemy ORM, proper HTTP status codes)
> - Use the correct formatter (`black`) and linter (`ruff`)
> - Distinguish safe commands (`make test`, `pytest`) from unsafe ones (`pip install`, `git push`)
> - Follow the prescribed TDD workflow when adding new endpoints
>
> **Steps taken to build it:**
> 1. Mapped out all files and their purposes in the starter app
> 2. Documented the project structure with file-by-file descriptions
> 3. Listed all run/test/format/lint commands
> 4. Defined coding conventions (Pydantic, SQLAlchemy, HTTP status codes, `Depends(get_db)`)
> 5. Classified commands into safe (auto-run) and unsafe (ask first) categories
> 6. Wrote a step-by-step workflow for adding a new API endpoint (test-first approach)
> 7. Documented current app status and what's missing

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run:** No explicit command needed. Simply launch Claude Code from the `week4/` directory:
> ```bash
> cd week4
> claude
> ```
> Claude Code automatically reads `CLAUDE.md` at session start and uses it as context for all subsequent interactions.
>
> **Expected output:** When you ask Claude to perform tasks (e.g., "add a DELETE endpoint for notes"), it will automatically:
> - Follow the TDD workflow (write test first, then implement, then format)
> - Use the correct project conventions (Pydantic schemas, proper status codes)
> - Run safe commands without asking, and prompt for unsafe commands
>
> **Rollback/safety notes:**
> - `CLAUDE.md` is a passive guidance file — it does not execute anything on its own
> - To roll back, simply delete or edit the file; changes take effect on the next Claude session
> - The "Unsafe Commands" section acts as a safety guardrail, preventing Claude from running destructive operations without explicit approval

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (manual):** Every time you start a Claude Code session, you would need to manually explain:
> - Where files are located (`backend/app/routers/notes.py`, `backend/tests/`, etc.)
> - What coding style to follow (black, ruff, Pydantic schemas)
> - Which commands are safe to run vs. which require confirmation  
> - The correct workflow order (test → implement → format → update docs)
> - What the app currently supports and what's missing
>
> This context would need to be repeated in every new session, leading to wasted time and inconsistent behavior.
>
> **After (automated):** Claude Code loads all of this context automatically at session start. It:
> - Immediately knows the project layout without needing to explore
> - Follows the TDD workflow consistently every time
> - Never runs `pip install` or `git push` without asking
> - Knows exactly which schemas, models, and routers exist
> - Can reference the "Current App Status" section to understand what's been built and what's left

e. How you used the automation to enhance the starter application
> I used the `CLAUDE.md` guidance to implement **Task #5 from `docs/TASKS.md`**: adding `PUT /notes/{id}` and `DELETE /notes/{id}` endpoints. When I prompted Claude Code with *"Add PUT and DELETE endpoints for notes following the workflow in CLAUDE.md"*, it automatically followed the prescribed TDD workflow:
>
> 1. **Wrote failing tests first** — Claude added 5 new test functions to `backend/tests/test_notes.py`: `test_update_note`, `test_update_note_not_found`, `test_partial_update_note`, `test_delete_note`, and `test_delete_note_not_found`.
> 2. **Ran `make test`** to confirm the tests failed (405 Method Not Allowed, as expected).
> 3. **Implemented the endpoints** in `backend/app/routers/notes.py` — added the `NoteUpdate` import, a `PUT /{note_id}` route with partial update support, and a `DELETE /{note_id}` route returning 204.
> 4. **Ran `make test`** again — all 8 tests passed.
> 5. **Ran `make format`** — code was already clean.
>
> The `CLAUDE.md` also helped Claude detect a missing `NoteUpdate` schema import issue and fix it by referencing the project structure section, which listed `schemas.py` as the home for Pydantic schemas. Without `CLAUDE.md`, Claude would have needed to explore the codebase manually to understand the project layout and conventions.


### Automation #2 — `/test-and-fix` Custom Slash Command
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by the [Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices) section on custom slash commands. The docs recommend creating reusable workflows as Markdown files in `.claude/commands/` for repeated tasks. The "Test runner with coverage" example in the assignment description (Example 1 under Section A) directly inspired this command. I combined the test-run, coverage-analysis, and auto-fix steps into a single idempotent workflow that can be invoked with `/test-and-fix`.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal:** Provide a one-command workflow that runs the full test suite, analyzes failures or coverage gaps, suggests fixes, and formats code — replacing a multi-step manual process.
>
> **Inputs:** Optional `$ARGUMENTS` — e.g., a specific test file path or pytest marker to scope the run (e.g., `/test-and-fix backend/tests/test_notes.py`).
>
> **Outputs:** A structured report containing either:
> - ✅ **All tests pass:** Coverage report with file-by-file line-missing details, 2-3 suggested test cases, and a summary table
> - ❌ **Tests fail:** For each failure: test name, assertion error, relevant buggy source code, proposed diff fix, and an offer to auto-apply fixes
>
> **Steps the command executes:**
> 1. Run `PYTHONPATH=. pytest -q backend/tests --maxfail=3 -x --tb=short` (with optional arguments)
> 2. If all pass → run coverage (`pytest --cov=backend/app --cov-report=term-missing`), summarize gaps, suggest new tests
> 3. If any fail → show test name + error + source code + proposed fix diff, ask to apply
> 4. After fixes applied → re-run tests to confirm green
> 5. Run `make format` to ensure code style compliance
> 6. Print a final summary table: tests run / passed / failed / coverage %

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run:** In a Claude Code session from the `week4/` directory:
> ```
> /test-and-fix
> ```
> Or with arguments to scope to specific tests:
> ```
> /test-and-fix backend/tests/test_notes.py
> ```
>
> **Expected output example (all pass):**
> ```
> ✅ All 8 tests passed!
>
> Coverage Report:
> | File                      | Stmts | Miss | Cover |
> |---------------------------|-------|------|-------|
> | backend/app/routers/notes.py | 30  | 2    | 93%   |
> | backend/app/schemas.py       | 15  | 0    | 100%  |
>
> Suggested tests to improve coverage:
> 1. Test updating a note with empty body (validation edge case)
> 2. Test search with special characters
> 3. Test creating a note with very long content
>
> | Metric       | Value |
> |--------------|-------|
> | Tests run    | 8     |
> | Tests passed | 8     |
> | Tests failed | 0     |
> | Coverage     | 85%   |
> ```
>
> **Rollback/safety notes:**
> - The command only reads and runs tests — it does not modify source code unless you explicitly approve a proposed fix
> - `make format` only applies deterministic formatting (black + ruff) which is safe and idempotent
> - If a proposed fix is wrong, simply decline it and make manual corrections
> - The `--maxfail=3 -x` flags stop early on failures to avoid noisy output

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (manual):** A typical test-fix cycle required multiple steps:
> 1. Manually run `pytest` and read raw output
> 2. Scroll through tracebacks to identify failures
> 3. Open each failing test and the relevant source file side-by-side
> 4. Mentally map the assertion error to the buggy line
> 5. Make a fix, re-run `pytest`
> 6. If all pass, manually run `pytest --cov` to check coverage
> 7. Interpret the coverage report to find gaps
> 8. Run `make format` to fix style
>
> This takes several minutes and requires context-switching between terminal and editor.
>
> **After (automated):** A single `/test-and-fix` command:
> 1. Runs the test suite automatically
> 2. Parses failures and pinpoints the exact source code + fix
> 3. Offers to apply fixes with a single confirmation
> 4. Re-verifies after applying
> 5. Runs coverage and highlights gaps with actionable suggestions
> 6. Formats code automatically
> 7. Produces a clean summary table
>
> The entire cycle is reduced to one command + one approval step.

e. How you used the automation to enhance the starter application
> I used `/test-and-fix` at two key points during development:
>
> 1. **Before implementing PUT/DELETE** — I ran `/test-and-fix` to establish a baseline. The command detected an `ImportError`: `notes.py` imported `NoteUpdate` from `schemas.py`, but that class didn't exist yet. The command automatically diagnosed the issue, added the missing `NoteUpdate` schema with `Optional[str]` fields, added the missing `from typing import Optional` import, re-ran the tests (3/3 passed), ran `make format`, and produced a clean summary table. This fixed a broken import that would have blocked all further development.
>
> 2. **After implementing PUT/DELETE** — I ran `/test-and-fix` again to verify the new endpoints. The command confirmed all 8 tests passed, then performed a manual coverage analysis (since `pytest-cov` was not installed). It produced a file-by-file coverage table showing that `notes.py` had full endpoint coverage, while `action_items.py` and `extract.py` had partial coverage. It suggested 3 specific test cases to improve coverage: testing 404 on action item completion, testing extract edge cases with empty strings, and testing `GET /notes/{id}` with a non-existent ID. The command ended with `make format` and a final summary table.
>
> In both cases, `/test-and-fix` replaced a manual multi-step process (run pytest → read tracebacks → fix → re-run → check coverage → format) with a single command that handled the entire cycle automatically.


### *(Optional) Automation #3*
*If you choose to build additional automations, feel free to detail them here!*

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> N/A

b. Design of each automation, including goals, inputs/outputs, steps
> N/A

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> N/A

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> N/A

e. How you used the automation to enhance the starter application
> N/A
