# Final AI Review and Ownership Evidence

## AGENTS.md guardrails
- Repo-specific stack and commands included: yes
- Docs-first/read-first guardrail included: yes
- Unexpected app/frontend edits rule included: yes

## AI code review mini-log

| AI comment | Grade: Useful / Noise / Wrong | Reason | Verification or decision |
|---|---|---|---|
| CLAUDE.md's Notes section documents the PATCH null-`title` rejection but has no matching bullet for null-`tags`, even though `app/models.py`'s `TaskUpdate.validate_tags` now rejects it identically | Useful | Confirmed asymmetry in the actual diff: `app/models.py` shows both validators raise on `None` identically, but `CLAUDE.md` only documented one | Added a "PATCH null-tags rule" bullet to `CLAUDE.md`'s Notes section (commit `b40b7a3`) |
| The branch mixes two unrelated bug fixes (naive-datetime overdue comparison, PATCH null-title/tags rejection) into the same diff as the Module 4 CI/Docker/docstring work | Noise | Diff does mix these, but each fix has its own commit and this is a single-branch course project, not a multi-team PR pipeline — a process observation, not a defect | None |
| The `docker-verify` health-check loop only retries for 10 seconds before failing the job, which could flake on a slower runner | Noise | No flakes observed across multiple real CI runs (health check passed on first attempt each time), but the window hasn't been stress-tested under load — absence of an observed problem, not a confirmed risk | None |
| `Dockerfile` hardcodes `python:3.11-slim` independently in both the builder and runtime `FROM` lines | Noise | Two literal `FROM python:3.11-slim` lines confirmed in the file, but it's a 25-line Dockerfile edited by hand — an `ARG` for one duplicated pin is more abstraction than the file's size/change frequency justifies | None |

## AI security mini-review

| Finding | File evidence | Grade: Valid / False Positive / Noise | Reason | Next action |
|---|---|---|---|---|
| Unbounded `description`/`assignee` string fields | `app/models.py` — `title`/`tags` each have a `field_validator`; `description`/`assignee` have none | Valid | Confirmed asymmetry directly in code | Add a `field_validator` length cap on `description`/`assignee` mirroring the existing `title`/`tags` pattern |
| No authentication/authorization on any route | `app/main.py` — no auth middleware or dependency on any route | Valid (course-scope gap, not a bug) | Intentional and documented in README/AGENTS.md, but would be a real production risk outside this course context | Keep documented as accepted risk for coursework; require an auth design before any real deployment |
| Lack of concurrency protection on shared in-memory store | `app/storage.py` — sync route handlers + non-atomic get→setattr→reassign on `_tasks`, no lock | Valid (identified by AI during reconciliation, not the original manual scan) | Confirmed via code inspection: Starlette dispatches sync `def` handlers to a threadpool, and the store mutation is not atomic | Add a lock around `_tasks` mutations, or explicitly document the single-writer assumption |
| CORS `allow_headers=["*"]` | `app/main.py` — CORS config | Noise | Origin is already locked to a single hardcoded value (`http://localhost:5500`); no real attack surface added by the permissive headers setting | None |

## Manual security check

I independently reviewed three areas the AI audit did not directly test: whether `app/main.py` leaks raw exception/stack-trace details to the client (confirmed it does not), whether `app/models.py`'s tag validation could be bypassed with malformed Unicode or unusually long strings (tested manually, found no bypass), and whether `frontend/index.html` uses `innerHTML` anywhere that could enable XSS (confirmed it consistently uses `textContent` instead). I also considered the business/deployment context directly — in-memory storage and the lack of concurrency protection are acceptable for this coursework project, but would become real concerns (data integrity, audit requirements, need for a real DB and auth) in an actual multi-user production deployment.

## One AI output I rejected or corrected

During Module 5.5's context-engineering exercise, Claude Code cited claims about repository content that it had not actually read via its file-reading tool in that session — it had used content auto-injected from `CLAUDE.md` as project instructions, but presented the claims without disclosing that source. This happened twice: once in Strategy A (the "minimal context" test, where it should not have had access to `CLAUDE.md` context) and once in Strategy C (the "targeted context" test, where it was told to read only three specific files and nothing else). In both cases I challenged the claims, asked for clarification, and required the Files Inspected list to be corrected before I accepted the drafts. I did not accept the AI's initial framing that these claims were "accurate" simply because the underlying content happened to be correct — the issue was that the sourcing was misrepresented, which is a trust problem independent of whether the specific facts were right.

## Three AI usage rules

1. Never paste: company passwords, API keys, customer personal information, or confidential company data into an AI tool.
2. Always verify: AI output against the actual files, test results, or command output before accepting it — never accept a summary as proof on its own.
3. Record AI contributions by: noting in commit messages and project docs what AI generated versus what I personally wrote, tested, or decided.

## Ownership statement

I am comfortable submitting this repository as my own work because every AI-generated claim, finding, and draft in it was checked against something real — actual file contents, actual test runs, actual CI logs, or actual command output — before I accepted it. Where AI findings were wrong, incomplete, or misrepresented their own sourcing (as with the CLAUDE.md leaks in Module 5.5), I caught and corrected them rather than passing them through. The security review, code review, and governance worksheets all reflect my own grading judgment, not AI's self-assessment. The personal AI playbook in `docs/ai-playbook.md` states rules I can actually defend with specific incidents from this course, not generic policy language. I understand the current scope and limitations of this app (no auth, no database, no deployment) well enough to explain them to a teammate, and I know which of the AI security findings are genuinely open risks versus accepted course-scope decisions.
