# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **Nguyen Minh Khanh** \
SUNet ID: **KhanhNguyen2712** \
Citations: **Anthropic Claude Code Best Practices (https://www.anthropic.com/engineering/claude-code-best-practices), Claude Code SubAgents overview (https://docs.anthropic.com/en/docs/claude-code/sub-agents), FastAPI docs (https://fastapi.tiangolo.com/), SQLAlchemy docs (https://docs.sqlalchemy.org/)**

This assignment took me about **6** hours to do. 


## YOUR RESPONSES
### Automation #1
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> I used the Claude Code best-practices guidance around repeatable workflows, idempotent commands, and explicit output formatting. The goal was to automate the most repetitive quality gate in this repo: run tests first, then lint only if tests pass.

b. Design of each automation, including goals, inputs/outputs, steps
> **Automation:** custom slash command `/.claude/commands/tests-gate.md` (invoked as `/tests-gate`).
> 
> **Goal:** standardize test + lint verification for Week 4 changes.
> 
> **Input:** optional `$ARGUMENTS` to scope pytest with `-k`.
> 
> **Output:** compact summary including pass/fail status, first failing error, and next step.
> 
> **Core steps:**
> 1) `cd week4`
> 2) run `PYTHONPATH=. pytest -q backend/tests --maxfail=1 -x` (or `-k "$ARGUMENTS"`)
> 3) if green, run `ruff check`
> 4) summarize results.

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run:**
> - `/tests-gate`
> - `/tests-gate notes`
>
> **Expected outputs:**
> - On success: “test gate passed”, modules touched, lint status.
> - On failure: first failing test + likely fix area.
>
> **Rollback/safety:**
> - Read-only for most runs; no destructive git operations.
> - Changes remain scoped to `week4/`.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before:** manually run different test/lint commands, inconsistent flags, and inconsistent summaries.
>
> **After:** one reusable command with stable flags and a consistent result format, reducing context-switch overhead and missed checks.

e. How you used the automation to enhance the starter application
> I used this automation while adding note CRUD + search improvements. It helped quickly validate each iteration of:
> - `GET /notes/search/` case-insensitive behavior,
> - `PUT /notes/{id}` and `DELETE /notes/{id}`,
> - schema validation updates,
> - expanded backend tests.


### Automation #2
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> I used the recommendation to reduce docs drift by making documentation maintenance a repeatable workflow. I also followed the idea of producing explicit deltas (added/changed/removed) for reviewability.

b. Design of each automation, including goals, inputs/outputs, steps
> **Automation:** custom slash command `/.claude/commands/docs-sync.md` (invoked as `/docs-sync`).
>
> **Goal:** keep `week4/docs/API.md` synchronized with actual routers/schemas.
>
> **Input:** optional `$ARGUMENTS` note for the changelog context.
>
> **Output:** route delta + changed-file checklist + follow-up TODOs.
>
> **Core steps:**
> 1) inspect `backend/app/routers/*.py` and `backend/app/schemas.py`
> 2) update `week4/docs/API.md`
> 3) emit route deltas and test suggestions.

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run:**
> - `/docs-sync`
> - `/docs-sync include validation changes`
>
> **Expected outputs:**
> - Added/changed/removed route summary
> - `API.md` updates reflecting request/response/validation behavior
>
> **Rollback/safety:**
> - Primary file is docs-only (`week4/docs/API.md`).
> - No runtime behavior changes unless explicitly requested.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before:** API docs often lagged behind code edits, requiring manual spot checks.
>
> **After:** one command gives a deterministic docs update checklist and drift summary.

e. How you used the automation to enhance the starter application
> After adding note update/delete/search improvements, I used this workflow to create/update `week4/docs/API.md`, documenting:
> - note search semantics,
> - new note update/delete endpoints,
> - validation and 404/422 error behavior.


### *(Optional) Automation #3*
*If you choose to build additional automations, feel free to detail them here!*

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by "repository guidance files" in Claude best practices. I converted recurring project context into always-on instructions to reduce setup repetition per conversation.

b. Design of each automation, including goals, inputs/outputs, steps
> **Automation:** repository-level `CLAUDE.md`.
>
> **Goal:** provide default execution map and safety rails for week4.
>
> **Input:** any coding request in this repo.
>
> **Output:** consistent behavior: scoped edits, test-first workflow, docs sync reminder.
>
> **Core content:**
> - run/test/format/lint commands,
> - file map for routers/tests/frontend,
> - endpoint-change workflow snippet,
> - non-destructive safety constraints.

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run:** open a new Claude Code session in this repository; `CLAUDE.md` is loaded automatically.
>
> **Expected outputs:** code changes that follow repo conventions, include tests/docs updates, and avoid unsafe commands.
>
> **Rollback/safety:** remove or edit `CLAUDE.md` if guidance becomes outdated.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before:** repeated manual instructions about project structure and command usage.
>
> **After:** persistent, centralized guidance that improves consistency across tasks.

e. How you used the automation to enhance the starter application
> I followed this guidance while implementing and validating the week4 enhancement set:
> - backend: case-insensitive note search + note update/delete + validation,
> - frontend: search/edit/delete note controls,
> - tests: expanded note/action-item coverage,
> - docs: new `week4/docs/API.md`.
