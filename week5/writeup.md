# Week 5 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **Nguyen Minh Khanh** \
SUNet ID: **TODO** \
Citations: **`week5/assignment.md`; `week5/README.md`; `week5/docs/TASKS.md`; Vercel FastAPI docs: https://vercel.com/docs/frameworks/backend/fastapi; Vercel project configuration docs: https://vercel.com/docs/project-configuration/vercel-json**

This assignment took me about **8** hours to do. 


## YOUR RESPONSES
### Automation A: Warp Drive saved prompts, rules, MCP servers

a. Design of each automation, including goals, inputs/outputs, steps
> I created a Warp Drive-style saved prompt named `week5-task-implementer`. The goal was to take one task number from `week5/docs/TASKS.md` and drive a repeatable loop of: read repo docs, summarize requirements, identify files to change, implement the task only inside `week5/`, run verification commands, and generate a short summary that could be copied into `report/task-XX.md` or `writeup.md`.
>
> Inputs:
> - `TASK_NUMBER`
> - an optional focus hint such as `backend-first`, `frontend-first`, or `verification-first`
>
> Outputs:
> - a short plan
> - code changes for the selected task
> - a final summary with changed files, behavior added, and test/lint results
>
> Steps:
> 1. Read `assignment.md`, `README.md`, `TASKS.md`, and the current code in `week5/`.
> 2. Restate the acceptance criteria for one task.
> 3. Make targeted edits.
> 4. Run `conda run -n cs146s make test` and `conda run -n cs146s make lint`.
> 5. If the task touched the React frontend, also run `npm test` and `npm run build` inside `week5/frontend`.
> 6. Emit a compact summary for documentation.
>
> I used this automation repeatedly for the API-first tasks: task 7 (response envelopes), task 8 (pagination), task 3 (notes CRUD), task 4 (action filters/bulk complete), task 2 (search/sort), task 5 (tags), task 6 (extraction), task 9 (indexes), and task 11 (deploy configuration).

b. Before vs. after (i.e. manual workflow vs. automated workflow)
> Before: for each task I would manually reopen the same markdown files, restate the requirements, decide which files mattered, run tests by hand, and then separately write down what changed.
>
> After: the saved prompt turned each task into the same deterministic flow. The prompt removed repeated context gathering and reduced the chance that I would forget repo constraints like “work only in `week5/`” or forget to run the verification commands before writing the report for that task.

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)
> I used medium autonomy. I allowed the automation to read and modify files inside `week5/`, run local verification commands, and prepare summaries. I did not treat commits or deployment as fully autonomous decisions; after each task I reviewed the changes, verified the branch state, and then committed one task at a time on `week5/khanh`. This level was appropriate because the automation could move quickly through repetitive implementation/verification work, but the repository still needed human supervision around task boundaries and commit granularity.

d. (if applicable) Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures
> This automation was mostly single-agent, so multi-agent behavior was not the main point here. The main coordination pattern was between implementation and verification: the saved prompt always ended in explicit test/lint/build output so I could decide whether a task was ready to commit.

e. How you used the automation (what pain point it resolves or accelerates)
> I used this automation as the default entry point for backend-heavy tasks where the main pain point was repetitive setup and verification rather than ideation. It accelerated tasks 7, 8, 2, 3, 4, 5, 6, and 9 because those tasks all followed the same rhythm: read requirement, change FastAPI/SQLAlchemy/Pydantic code, run tests, then summarize what changed. The automation also helped for task 11 because deploy config work is easy to do sloppily unless the repo checklist is repeated every time.



### Automation B: Multi‑agent workflows in Warp 

a. Design of each automation, including goals, inputs/outputs, steps
> I designed a multi-agent Warp workflow called `week5-multi-agent-coordinator`. The goal was to split larger tasks into independent streams in separate Warp tabs so that backend, frontend, and review work could proceed concurrently without clobbering each other.
>
> Roles:
> - `lead`: reads the task and assigns scopes
> - `backend`: owns FastAPI routes, models, schemas, extraction logic, and backend tests
> - `frontend`: owns React UI, component wiring, and browser-facing behavior
> - `review`: reruns verification commands and checks for missing cases
>
> Inputs:
> - `TASK_NUMBER`
> - current repo state
>
> Outputs:
> - one scoped plan per role
> - a merge order
> - final verification notes and write-up bullets
>
> Steps:
> 1. In the lead tab, summarize the task and split files/responsibilities.
> 2. Run backend and frontend tabs in parallel on disjoint file sets.
> 3. Use a review tab to run `make test`, `make lint`, `npm test`, and `npm run build` as needed.
> 4. Merge the work, resolve edge cases, and then commit one finished task.
>
> This workflow was the best fit for task 1 (Vite + React migration), task 10 (coverage improvements across backend and frontend), and parts of task 11 (frontend build + backend function packaging).

b. Before vs. after (i.e. manual workflow vs. automated workflow)
> Before: large tasks such as the React migration forced me to context-switch constantly between Python routes, UI wiring, component tests, build tooling, and final verification. Even when the code changes were conceptually separate, I still had to mentally serialize them.
>
> After: the multi-agent workflow let me treat the task as coordinated parallel lanes. The backend lane stabilized API contracts, the frontend lane migrated UI behavior onto React/Vite, and the review lane checked that integration still held together. That reduced idle time and made it easier to reason about ownership of each file set.

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)
> I used asymmetric autonomy. The backend and frontend workers had permission to edit only their own slices of `week5/`, while the review worker was effectively read-mostly plus verification commands. I supervised the merge points manually, especially when a frontend change depended on a backend response shape. This was important for task 1 because the frontend migration depended on stable API envelopes, pagination payloads, tags, and extraction routes from earlier tasks.

d. (if applicable) Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures
> Roles and coordination:
> - backend: API contracts, models, tests
> - frontend: React components, Vite config, UI behavior
> - review: test/lint/build validation
>
> Concurrency wins:
> - task 1 was much easier once UI migration and API-compatibility checks were split
> - task 10 benefited from parallel backend error-path coverage and frontend integration tests
>
> Risks:
> - conflicting assumptions about response shapes
> - duplicated work if two tabs touched the same file
> - stale context after one lane changed a shared contract
>
> Failures/lessons:
> - the safest pattern was to keep ownership disjoint and have the lead tab define the merge order up front
> - review had to be a separate lane; otherwise it was too easy to skip frontend build verification after backend tests were already green

e. How you used the automation (what pain point it resolves or accelerates)
> I used this automation when the work naturally split across different surfaces of the repo. It resolved the pain point of “one large task with multiple independent subproblems.” For example, the React migration needed UI component work, static asset/build changes, FastAPI serving changes, and final verification. Running those as coordinated roles was much faster and less error-prone than keeping everything in one linear tab.


### (Optional) Automation C: Any Additional Automations
a. Design of each automation, including goals, inputs/outputs, steps
> I also used a smaller verification/release-style automation focused on end-of-task checks. Conceptually, this was a Warp workflow that accepted a task number or task label and then ran the exact verification surface needed for that task:
> - backend-only tasks: `conda run -n cs146s make test` and `make lint`
> - frontend-affecting tasks: the above plus `cd week5/frontend && npm test && npm run build`
> - deployment task: verify `vercel.json`, `api/index.py`, `requirements.txt`, and that FastAPI serves the built frontend bundle correctly
>
> The output was a concise pass/fail summary and a short markdown snippet for the corresponding `report/task-XX.md`.

b. Before vs. after (i.e. manual workflow vs. automated workflow)
> Before: verification was easy to do inconsistently. Some tasks only needed Python checks, while others required both Python and Node verification, and deployment work required one more layer of sanity checking.
>
> After: the verification workflow encoded the correct command set per task type, so I was less likely to forget `npm run build` after frontend changes or forget to verify the backend still served `frontend/dist`.

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)
> This automation ran at relatively low autonomy. It mainly executed commands and summarized outputs; it did not decide on large code changes by itself. I supervised the results directly and used them as the gate before creating each per-task commit.

d. (if applicable) Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures
> This workflow was usually single-agent. Its value was not parallelism but consistency. The main coordination benefit was acting as the final gate after the implementation lanes finished.

e. How you used the automation (what pain point it resolves or accelerates)
> I used this most heavily on task 1, task 10, and task 11 because those tasks crossed both Python and frontend tooling. It accelerated the last mile of the work: instead of manually deciding “what should I rerun for this task,” I had a fixed verification routine that matched the scope of the changes.
