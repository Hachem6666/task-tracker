# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 1. Tech Stack

- Python 3.11+ (README: "Python 3.11 or newer")
- FastAPI 0.110.0 (`requirements.txt`) [VERIFY exact installed version matches this pin — not confirmed against the active environment]
- Pydantic v2 (`pydantic>=2.9.2`; v2 API — `ConfigDict`, `field_validator` — used throughout `app/models.py`)
- Uvicorn 0.29.0 (`requirements.txt`) [VERIFY exact installed version matches this pin — not confirmed against the active environment]
- pytest — test suite lives in `tests/` and uses pytest, but pytest is **not** listed in `requirements.txt` [VERIFY exact pinned version — this environment has 8.4.2 installed, but it isn't declared as a project dependency]
- httpx<0.28 (`requirements.txt`) — used by Starlette's `TestClient` (exposed via `fastapi.testclient`) in tests
- python-dotenv 1.0.1 (`requirements.txt`) — loads `.env` in `app/main.py` [VERIFY exact installed version matches this pin — not confirmed against the active environment]
- Vanilla JavaScript frontend (`frontend/index.html`) — single file, no framework, no build step

## 2. Run Command

```bash
uvicorn app.main:app --reload --port 8000
```

## 3. Test Command

```bash
pytest -v
```

## 4. Architecture Summary

**Backend** (`app/`):
- `app/main.py` — FastAPI app instance, CORS middleware, and all routes (`/health`, `/tasks`, `/tasks/{task_id}`).
- `app/models.py` — Pydantic models: `TaskCreate`, `TaskUpdate`, `TaskResponse`, `TaskStatus` (enum), `TaskPriority` (enum). Field-level validation (title trim/length, tag trim/length/count) lives here via `field_validator`.
- `app/business_rules.py` — `validate_status_transition()` and `VALID_TRANSITIONS`. **This is where task status transition rules live.**
- `app/storage.py` — In-memory store (`_tasks: dict[str, TaskResponse]`), module-level global, no database. Also implements filtering (status, priority, overdue, tag) at read time.

**Frontend**:
- `frontend/index.html` — single-file vanilla JS Kanban board: drag-and-drop, create/edit modal, board-level and modal-level UI states.

**Tests** (`tests/`):
- `tests/test_tasks.py` — pytest suite covering CRUD, status transitions, filters, due dates, tags.
- `tests/conftest.py` — fixtures: `client`, `created_task`, autouse `_reset_storage` (clears in-memory store between tests).
- `tests/verify_a.py` — standalone model-validation script; not pytest-discovered (its functions aren't `test_`-prefixed).

**Where task rules live**: status-transition rules → `app/business_rules.py`; field-level validation (title, tags) → `app/models.py`; filtering/derived rules (overdue, tag match) → `app/storage.py`.

## 5. Business Rules

**Task status values** (`TaskStatus` enum, `app/models.py`):
- `ToDo`
- `InProgress`
- `Done`

**Status transition rules** (`VALID_TRANSITIONS`, `app/business_rules.py`):
- `ToDo` → `InProgress`
- `InProgress` → `Done`
- `Done` → `InProgress`
- Any transition not in this set — including same→same (e.g. `ToDo` → `ToDo`) — is rejected with `422 Unprocessable Entity` and an error message listing the allowed transitions.

Transition validation is checked in the `PATCH /tasks/{task_id}` route handler (`app/main.py`), before `storage.update_task` is called, because it needs the task's *current* status to validate against the requested new status.

## 6. UI States and CORS Notes

**CORS** (`app/main.py`):
- `allow_origins=["http://localhost:5500"]` — only this exact origin is permitted.
- `allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"]`
- `allow_headers=["*"]`
- Practical implication: the frontend must be served from `http://localhost:5500` (e.g. `python -m http.server 5500 --directory frontend`). A mismatched origin being blocked is standard browser CORS enforcement, not behavior this repo's own tests exercise or verify.

**UI states** (`frontend/index.html`, `setBoardState()`):
- `loading` — shown while `fetchTasks()` is in flight ("Loading tasks…").
- `empty` — shown when the task list loads with zero tasks.
- `error` — shown on fetch/network failure; rendered with `role="alert"`.
- `ready` — shown once tasks have loaded successfully.

The create/edit modal has its own separate inline error state (`.modal__error`, `.field-error` / `titleError`) for form-validation feedback, distinct from the board-level state above.

## 7. Do-Not Rules

- Do not add authentication/authorization.
- Do not add a database or persistence layer.
- Do not add deployment steps or config (hosting, orchestration, CI/CD publishing).
- CI is limited to test-only workflows (e.g. `.github/workflows/ci.yml` running `pytest -v` on push/PR). Do not add deployment, publishing, or release steps to CI without asking first.
- A local build/run Dockerfile and `.dockerignore` are permitted (containerizing the app for local use). Do not add orchestration (docker-compose, Kubernetes), a registry push, or hosting config without asking first.
- Do not make major UI changes (new pages, redesigns, new frameworks) without asking first.

## Notes

- **PATCH null-title rule**: `title` cannot be explicitly set to `null` on `PATCH /tasks/{task_id}` — the `TaskUpdate` validator in `app/models.py` rejects it with `422`. Omitting `title` from the PATCH body leaves it unchanged (`model_dump(exclude_unset=True)` in `app/storage.py`); only an explicit `null` is rejected.
- **Overdue is computed, not stored**: a task is overdue if `due_date` is in the past AND `status != Done`. This is recalculated on every read in `app/storage.py` rather than persisted, so it's always consistent with current time and status.
- **Naive vs. aware datetime handling**: incoming `due_date` values may be timezone-naive; `storage._as_aware_utc()` normalizes to UTC-aware before comparing against `datetime.now(timezone.utc)` in the overdue filter. See regression test `test_list_tasks_filter_overdue_with_naive_due_date_does_not_crash` in `tests/test_tasks.py`.
- **`docs/midcourse/`** contains the user stories, mini-ADR (design decisions/alternatives considered/rejected scope), prompt log, verification evidence, and reflection for the mid-course extension. Consult the mini-ADR before changing due-date or tag behavior — it records what was deliberately left out of scope (recurring due dates, timezone-specific handling, shared tag tables, etc.).
