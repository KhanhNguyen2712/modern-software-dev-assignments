# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **Anthropic Claude Code documentation (claude.ai/docs), Anthropic Sub-agents documentation**

This assignment took me about **5** hours to do. 


## YOUR RESPONSES
### Automation #1: CLAUDE.md Guidance File

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by Claude Code's persistent memory system and the best-practice of "Context is Everything" from the sub-agents documentation. CLAUDE.md provides immediate context without requiring repetitive explanations at the start of each session. Similar to how `.cursorrules` or `.claude/config` files work in other AI-assisted development tools.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal:** Provide instant project context to Claude Code, eliminating setup time and ensuring consistent adherence to project conventions.
>
> **Inputs:** None (static file)
> 
> **Outputs:** Contextual awareness for Claude Code
>
> **Steps:**
> 1. Document project structure (stack, file locations, patterns)
> 2. Define coding rules (TDD workflow, import patterns)
> 3. Place at `week4/CLAUDE.md` for automatic loading
> 4. Update as project evolves
>
> **Contents:**
> - Stack: FastAPI + SQLite, pytest, black + ruff
> - Structure: Router/model/schema locations
> - Import patterns: `from ..db import get_db`, `from ..schemas import NoteCreate`
> - Coding rules: TDD first, format before commit, 6-step endpoint workflow

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run:**
> - CLAUDE.md is automatically loaded by Claude Code when present in the working directory
> - No manual commands needed
>
> **Expected outputs:**
> - Claude Code immediately knows project structure
> - Correct import suggestions without prompting
> - TDD workflow adherence
>
> **Rollback/Safety:**
> - File is version controlled (git)
> - Can be deleted or renamed to disable
> - Non-destructive (only provides context)

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (manual):**
> ```
> User: "Add DELETE endpoint for notes"
> Claude: "What framework are you using? Where are the routers? 
>          What's the import pattern? What's the testing setup?"
> User: [Explains project structure...]
> Claude: [Finally starts working]
> ```
>
> **After (with CLAUDE.md):**
> ```
> User: "Add DELETE endpoint for notes"
> Claude: [Already knows to write test first, use NoteRead schema, 
>          return {"message": "..."}, follow existing patterns]
> ```
>
> **Time saved:** ~5-10 minutes per session startup

e. How you used the automation to enhance the starter application
> - **DELETE /notes/{id}:** Used CLAUDE.md context to immediately write test following TDD pattern, then implement endpoint with correct imports and error handling (404 for not found)
> - **PUT /notes/{id}:** Leveraged import patterns from CLAUDE.md to add NoteUpdate schema and update endpoint without trial-and-error
> - **NoteUpdate schema:** Followed existing schema patterns documented in CLAUDE.md
>
> All features passed tests and followed project conventions without requiring explanation.


### Automation #2: SubAgents Pipeline (PowerShell)

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Inspired by Anthropic's Sub-agents documentation (claude.ai/docs/agents) and the Unix philosophy of "do one thing well." The pipeline implements the "Divide and Conquer" pattern, with specialized agents for testing, coding, and documentation. Also follows the "TDD Workflow" best-practice of writing tests before implementation.

b. Design of each automation, including goals, inputs/outputs, steps
> **Goal:** Automate the TDD workflow by orchestrating specialized sub-agents that handle testing, implementation, and documentation in sequence.
>
> **Components:**
> 1. **test-agent.ps1** - Creates failing tests (TDD)
> 2. **code-agent.ps1** - Implements features to pass tests
> 3. **docs-agent.ps1** - Generates API documentation
>
> **test-agent.ps1:**
> - Inputs: Feature description, router path, schema requirements
> - Outputs: Failing test file
> - Steps:
>   1. Read existing test patterns
>   2. Generate test function with assertions
>   3. Run pytest to confirm failure
>
> **code-agent.ps1:**
> - Inputs: Failing test file, router/schema paths
> - Outputs: Passing implementation
> - Steps:
>   1. Read test requirements
>   2. Implement endpoint/schema
>   3. Run pytest to confirm pass
>
> **docs-agent.ps1:**
> - Inputs: Router files
> - Outputs: docs/API.md
> - Steps:
>   1. Parse @router decorators
>   2. Extract methods, paths, responses
>   3. Generate markdown with examples

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> **How to run:**
> ```powershell
> # Run individual agents
> .\automations\test-agent.ps1 -Feature "DELETE endpoint" -Router "notes.py"
> .\automations\code-agent.ps1 -TestFile "test_notes.py" -Router "notes.py"
> .\automations\docs-agent.ps1 -Routers "routers/*.py" -Output "docs/API.md"
> 
> # Or run orchestrator
> .\automations\orchestrator.ps1 -Feature "DELETE endpoint" -Router "notes.py"
> ```
>
> **Expected outputs:**
> ```
> [TEST-AGENT] Created test_delete_note_success in test_notes.py
> [TEST-AGENT] Confirmed test fails with 405 Method Not Allowed
> 
> [CODE-AGENT] Added DELETE /notes/{note_id} endpoint to notes.py
> [CODE-AGENT] All tests passing (5/5)
> 
> [DOCS-AGENT] Documented 9 endpoints across 2 routers
> [DOCS-AGENT] Saved to docs/API.md
> ```
>
> **Rollback/Safety:**
> - All changes are git-tracked
> - Agents work in isolation (separate files)
> - Tests prevent broken code from being considered "done"
> - Can run `git reset --hard` to undo

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **Before (manual TDD):**
> ```
> 1. User: Write test for DELETE endpoint
> 2. User: Run pytest to confirm it fails
> 3. User: Implement DELETE endpoint
> 4. User: Run pytest to confirm it passes
> 5. User: Update API documentation
> 6. User: Run format and lint
> Time: ~20-30 minutes
> ```
>
> **After (with SubAgents):**
> ```
> 1. User: Run test-agent (creates failing test)
> 2. User: Run code-agent (implements feature)
> 3. User: Run docs-agent (updates documentation)
> Time: ~5-10 minutes
> ```
>
> **Improvements:**
> - Parallel work: docs-agent can run while code-agent works
> - Consistency: agents follow patterns exactly
> - Focus: user only reviews, doesn't type boilerplate
>
> **Time saved:** ~60-70% reduction in repetitive typing

e. How you used the automation to enhance the starter application
> Used the SubAgents pipeline to implement three features:
>
> **1. DELETE /notes/{note_id}:**
> - test-agent: Created `test_delete_note_success` and `test_delete_note_not_found`
> - code-agent: Implemented delete endpoint with 404 handling
> - Result: Tests pass, endpoint returns `{"message": "Note deleted successfully"}`
>
> **2. PUT /notes/{note_id} + NoteUpdate schema:**
> - test-agent: Created `test_update_note_success` and `test_update_note_not_found`
> - code-agent: Added `NoteUpdate` schema and update endpoint
> - Result: Full update functionality with validation
>
> **3. API Documentation:**
> - docs-agent: Generated complete `docs/API.md` with 9 endpoints documented
> - Includes: Request/response examples, status codes, schemas
>
> **Final Results:**
> ```bash
> $ pytest -q backend/tests
> .......
> 7 passed, 4 warnings in 0.23s
> ```
> All features working, all tests passing, documentation current.


### *(Optional) Automation #3*
*If you choose to build additional automations, feel free to detail them here!*

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> N/A - Only built 2 automations for this assignment

b. Design of each automation, including goals, inputs/outputs, steps
> N/A

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> N/A

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> N/A

e. How you used the automation to enhance the starter application
> N/A
