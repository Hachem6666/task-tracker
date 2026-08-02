# Security Review: Module 5 (AI Findings + Manual Scan Reconciliation)

Source: AI-assisted read-only security audit (findings S1-S5) of the Task Tracker repo, graded by the student, then reconciled against an independent manual security scan.

## AI Findings, as Graded

| ID | Finding | Grade | Reason |
|---|---|---|---|
| S1 | Unbounded `description`/`assignee` string fields (`app/models.py`) — no length validator, unlike `title`/`tags` | Valid | Confirmed asymmetry in code: `title` and `tags` each have a `field_validator`; `description`/`assignee` have none |
| S2 | Unbounded task count / memory growth (`app/storage.py`) | Noise | Documented in-memory design (`README.md`, `CLAUDE.md` §7); only actionable if deployment scope changes |
| S3 | No authentication/authorization on any route | Valid (course-scope gap, not a bug) | Intentional and documented (`README.md`, `CLAUDE.md` §7); recorded as Valid-with-a-note because it would be a real production risk outside this course context |
| S4 | Inconsistent dependency pinning (`pydantic>=2.9.2`, `httpx<0.28` vs. exact pins on fastapi/uvicorn) | Noise | No CVE evidence collected; `CLAUDE.md`'s existing `[VERIFY]` flags on these packages already track this |
| S5 | CORS `allow_headers=["*"]` | Noise | Origin already locked to a single hardcoded value (`http://localhost:5500`); no real attack surface added |

## Manual Scan Findings

1. `app/main.py` error handling — confirmed no raw exception/stack-trace leakage to the client
2. `app/models.py` tags validation — confirmed no bypass via malformed Unicode or long strings
3. `frontend/index.html` — confirmed `textContent` used (not `innerHTML`), no XSS injection point
4. Business logic / deployment context — in-memory storage and lack of concurrency protection are acceptable for this coursework project, but would become significant concerns (audit requirements, data integrity, need for a real DB/auth/authz) in a real multi-user Africell production environment

## Reconciliation

| Agreement | AI-only | You-only | AI-identified during reconciliation |
|---|---|---|---|
| **No auth is a production-relevance gap** — AI: S3 (Valid, course-scope note). Manual: item #4 ties absence of auth/authz directly to a real Africell multi-user deployment. | **S1 — unbounded `description`/`assignee` fields** — not raised in the manual scan. | **Tags validation robustness against malformed Unicode/long-string bypass** — manually tested; AI's S1 only read the validator source (strip + length check) and never reasoned about encoding-level bypass. *Needs evidence*: specific test inputs used were not logged, so this is not independently confirmed. | **Concurrency / race conditions on shared in-memory store** — surfaced by AI during reconciliation, not from the manual scan. Route handlers in `app/main.py` are sync `def` (confirmed via inspection), which Starlette dispatches to a threadpool; `storage.update_task` (`app/storage.py:120-130`) does a non-atomic get→setattr→reassign with no lock. Related in spirit to manual item #4's general "data integrity" concern, but the specific mechanism was identified by AI, not the student. |
| **In-memory storage is acceptable for coursework, not production** — AI: S2 (Noise, "only actionable if deployment scope changes"). Manual: item #4 ("acceptable for coursework... would become significant in real multi-user Africell production — audit requirements, data integrity"). | **S4 — inconsistent dependency pinning** — not raised in the manual scan. | | |
| **No raw stack-trace/exception leakage to the client** — AI: audit's "clean categories" list. Manual: item #1, same conclusion. | **S5 — CORS `allow_headers=["*"]`** — not raised in the manual scan. | | |
| **No frontend XSS injection point** — AI: audit's "clean categories" list (`textContent`, not `innerHTML`). Manual: item #3, identical conclusion and identical evidence. | | | |

### Observation on AI coverage shape

AI's coverage clustered around static, read-the-code checks — validator presence/absence, config values, pinning strings — and was accurate where it looked, but it never simulated adversarial input (Unicode/bypass testing) or reasoned about runtime concurrency behavior across requests. Both gaps required stepping outside "does the code do what it says" into "what happens under hostile or concurrent input" — one caught by manual review, one surfaced by AI only once prompted to reconcile, not in its original pass.

## Top-3 Security Backlog (from Valid findings)

| Rank | Finding | Why it matters | Suggested owner | Next action |
|---|---|---|---|---|
| 1 | No authentication/authorization (S3, Valid) | Course-scope now, but explicitly flagged by manual review as a blocker for any real multi-user Africell deployment — data belonging to any user is readable/writable/deletable by anyone with network access. | Course/project owner (scope decision) → backend (implementation if scope changes) | Keep documented as accepted risk for coursework; if this app is ever considered for real use, require an auth design (e.g. session or token-based) before further feature work. |
| 2 | Lack of concurrency protection on shared in-memory store (AI-identified during reconciliation, not from manual scan) | Sync route handlers + non-atomic dict read-modify-write in `storage.py` create a real data-integrity risk (lost updates, TOCTOU on delete-vs-update races) under concurrent requests. | Backend | Add a lock around `_tasks` mutations in `storage.py`, or explicitly document single-writer assumption as a course-scope limitation if not fixing now. |
| 3 | Unbounded `description`/`assignee` string fields (S1, Valid) | Asymmetric validation — `title`/`tags` are capped, sibling free-text fields are not — is a concrete, low-effort gap confirmed directly in `app/models.py`. | Backend | Add a `field_validator` length cap on `description`/`assignee` mirroring the existing `title`/`tags` pattern. |
