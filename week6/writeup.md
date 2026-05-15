# Week 6 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **Khanh Nguyen** \
SUNet ID: **TODO** \
Citations: **Antigravity AI coding assistant (Gemini-based) was used to analyze Semgrep findings, suggest fixes, and generate code diffs.**

This assignment took me about **2** hours to do.


## Brief findings overview
> Semgrep scan (`semgrep ci --subdir week6`) reported **38 findings** across three categories:
>
> **SAST (Code Analysis) — 12 non-blocking findings:**
> - SQL Injection: 4 findings related to `sqlalchemy.text()` with f-string interpolation and unsanitized `skip`/`limit` parameters in `notes.py` and `action_items.py`
> - Code Injection: 2 findings for `eval()` usage in `debug_eval` endpoint (`notes.py:104`)
> - Command Injection: 2 findings for `subprocess.run(shell=True)` in `debug_run` endpoint (`notes.py:112`)
> - SSRF: 1 finding for `urlopen()` with unvalidated URL in `debug_fetch` (`notes.py:120`)
> - Path Traversal: 1 finding for unvalidated file path in `debug_read` (`notes.py:128`)
> - Wildcard CORS: 1 finding for `allow_origins=["*"]` in `main.py:24`
>
> **Secrets — Not explicitly flagged in this scan configuration**, but a hardcoded API token (`sk_live_...`) was manually identified in `extract.py:13`.
>
> **SCA (Supply Chain) — 26 findings:**
> - 1 Reachable: Werkzeug CVE-2024-34069 (CSRF, HIGH)
> - 17 Undetermined: CVEs in pydantic, requests, jinja2, werkzeug (MODERATE/LOW)
> - 8 Unreachable: CVEs in requests, pyyaml (CRITICAL), werkzeug (HIGH/MODERATE)
>
> **False positives / noisy rules ignored:**
> - `generic-sql-fastapi` flagged `notes.py:33` and `action_items.py:33` for using `stmt.offset(skip).limit(limit)` where `skip` and `limit` are typed `int` parameters. These are false positives because SQLAlchemy's ORM `.offset()` and `.limit()` methods accept integer values and are not vulnerable to SQL injection — the values are parameterized by the ORM automatically.

## Fix #1
a. File and line(s)
> `week6/backend/app/routers/notes.py`, lines 69–92 (the `unsafe_search` endpoint)

b. Rule/category Semgrep flagged
> - `python.sqlalchemy.security.audit.avoid-sqlalchemy-text.avoid-sqlalchemy-text` (line 71–79)
> - `python.fastapi.db.sqlalchemy-fastapi.sqlalchemy-fastapi` (line 72–78)
> - `python.fastapi.db.generic-sql-fastapi.generic-sql-fastapi` (line 80)
>
> Category: **SAST — SQL Injection**

c. Brief risk description
> The `unsafe_search` endpoint builds a SQL query using an f-string that directly interpolates the user-supplied query parameter `q` into the SQL statement: `WHERE title LIKE '%{q}%'`. This allows an attacker to inject arbitrary SQL — for example, passing `q = "' OR 1=1 --"` would return all rows, and more sophisticated payloads could extract or modify data.

d. Your change (short code diff or explanation, AI coding tool usage)
> Used Antigravity AI to refactor the raw SQL from an f-string to a parameterized query using SQLAlchemy's `text()` bind parameters:
> ```diff
>  sql = text(
> -    f"""
> +    """
>      SELECT id, title, content, created_at, updated_at
>      FROM notes
> -    WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
> +    WHERE title LIKE :pattern OR content LIKE :pattern
>      ORDER BY created_at DESC
>      LIMIT 50
>      """
>  )
> -rows = db.execute(sql).all()
> +rows = db.execute(sql, {"pattern": f"%{q}%"}).all()
> ```

e. Why this mitigates the issue
> Parameterized queries (bind parameters) ensure that user input is treated as **data**, not as part of the SQL command structure. The database driver escapes the value of `:pattern` automatically, so even if `q` contains SQL metacharacters like `'`, `--`, or `;`, they are treated as literal string content rather than SQL syntax. This completely prevents SQL injection attacks on this endpoint.

## Fix #2
a. File and line(s)
> `week6/backend/app/services/extract.py`, line 13

b. Rule/category Semgrep flagged
> While this was not explicitly flagged by Semgrep's code rules in this scan (secrets rules may not have been enabled), the hardcoded token `sk_live_51HACKED_EXAMPLE_DO_NOT_USE_abcdefghijklmnopqrstuvwxyz` is clearly a **Secrets** category issue — a hardcoded API credential in source code.

c. Brief risk description
> A hardcoded API token in source code gets committed to version control, where it can be discovered by anyone with repository access (or through leaked repos). An attacker with this token could impersonate the application, access paid services, or perform unauthorized actions on the associated account (e.g., Stripe charges if this were a real key).

d. Your change (short code diff or explanation, AI coding tool usage)
> Used Antigravity AI to replace the hardcoded token with an environment variable lookup:
> ```diff
> +import os
> +
>  def extract_action_items(text: str) -> list[str]:
>      ...
>
> -API_TOKEN = "sk_live_51HACKED_EXAMPLE_DO_NOT_USE_abcdefghijklmnopqrstuvwxyz"
> +API_TOKEN = os.environ.get("API_TOKEN", "")
> ```

e. Why this mitigates the issue
> Moving the secret to an environment variable ensures it is never stored in version control. The actual token value is supplied at runtime through the deployment environment (e.g., `.env` file excluded via `.gitignore`, CI/CD secrets, or a secrets manager). This follows the 12-factor app principle of storing config in the environment. Additionally, the old token should be **rotated/revoked** since it was previously committed.

## Fix #3
a. File and line(s)
> `week6/backend/app/routers/notes.py`, lines 108–113 (the `debug_run` endpoint)

b. Rule/category Semgrep flagged
> - `python.fastapi.os.tainted-os-command-stdlib-fastapi-secure-default.tainted-os-command-stdlib-fastapi-secure-default` (line 112)
> - `python.lang.security.audit.subprocess-shell-true.subprocess-shell-true` (line 112)
>
> Category: **SAST — Command Injection**

c. Brief risk description
> The `debug_run` endpoint passes user-supplied input directly to `subprocess.run(cmd, shell=True)`. With `shell=True`, the command is interpreted by the system shell (`/bin/sh`), which means an attacker can inject arbitrary shell commands. For example, `cmd = "ls; cat /etc/passwd"` would execute both commands. This is a **Remote Code Execution (RCE)** vulnerability — an attacker gains full control of the server.

d. Your change (short code diff or explanation, AI coding tool usage)
> Used Antigravity AI to replace `shell=True` with `shell=False` and `shlex.split()` for safe argument parsing:
> ```diff
> +import shlex
>  ...
>
>  @router.get("/debug/run")
>  def debug_run(cmd: str) -> dict[str, str]:
>      import subprocess
>
> -    completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)  # noqa: S602,S603
> +    completed = subprocess.run(shlex.split(cmd), shell=False, capture_output=True, text=True)
>      return {"returncode": str(completed.returncode), ...}
> ```

e. Why this mitigates the issue
> Setting `shell=False` means the command is executed directly without invoking a system shell. `shlex.split()` safely tokenizes the command string into a list of arguments (e.g., `"ls -la /tmp"` → `["ls", "-la", "/tmp"]`) without interpreting shell metacharacters like `;`, `|`, `&&`, or `$()`. This prevents shell injection because special characters are passed as literal arguments to the program, not interpreted as shell operators. While a debug endpoint like this should ideally be removed entirely in production, this fix eliminates the immediate command injection vector.