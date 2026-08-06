# Task Tracker — Architecture Overview

## 1. What the app does
Task Tracker is a single-user Kanban-style task manager: a FastAPI backend exposes CRUD endpoints for tasks (with status transitions, due dates, priorities, and tags), and a vanilla-JS frontend renders them as a drag-and-drop board across ToDo / InProgress / Done columns. There is no database (in-memory storage) and no authentication.

## 2. Data model
Core entity: **Task** (`TaskResponse` in `app/models.py`):
- `id` (str, UUID4), `title` (str, 1–200 chars, trimmed), `description` (str)
- `status`: `ToDo` | `InProgress` | `Done` (enum)
- `priority`: `Low` | `Medium` | `High` (enum)
- `assignee` (optional str), `due_date` (optional datetime)
- `tags` (list[str], max 10, each 1–30 chars, trimmed)
- `created_at`, `updated_at` (UTC datetimes, server-set)

Separate input models `TaskCreate` (POST) and `TaskUpdate` (PATCH, all fields optional) apply the same field-level validation before a `TaskResponse` is built or mutated.

## 3. Request flow — creating a task
1. Frontend submits `POST /tasks` with a JSON body (`frontend/index.html`, `API_BASE_URL = http://localhost:8000`).
2. FastAPI parses/validates the body into `TaskCreate` (`app/models.py`); `field_validator`s trim/reject bad `title`/`tags`. Failure → `422` before the route body runs.
3. `create_task()` in `app/main.py` calls `storage.add_task(payload)`.
4. `app/storage.py.add_task` generates a UUID `id`, sets `created_at`/`updated_at` to `datetime.now(timezone.utc)`, builds a `TaskResponse`, and stores it in the module-level `_tasks` dict.
5. `TaskResponse` (id included) is returned with `201 Created`; the frontend refreshes the board from the response.

## 4. Key files
- `app/main.py` — FastAPI app instance, CORS config, all five routes (`/health`, `/tasks` GET/POST, `/tasks/{id}` GET/PATCH/DELETE).
- `app/models.py` — Pydantic v2 models and field-level validation (title, tags).
- `app/business_rules.py` — `VALID_TRANSITIONS` and `validate_status_transition()`, the sole source of status-transition rules.
- `app/storage.py` — in-memory `_tasks` dict; CRUD plus read-time filtering (status, priority, overdue, tag) and naive→UTC datetime normalization.
- `frontend/index.html` — single-file vanilla-JS Kanban UI (drag-and-drop, create/edit modal, board states).
- `tests/test_tasks.py` — pytest suite: CRUD, transitions, filters, due dates, tags.
- `tests/conftest.py` — `client`/`created_task` fixtures and autouse storage reset between tests.

## 5. Conventions
- **Validation**: field-level rules (title, tags) live in `app/models.py` via `field_validator`; both `TaskCreate` and `TaskUpdate` reject unknown fields (`extra="forbid"`). `TaskUpdate` additionally rejects explicit `null` for `title`/`tags`, while omitting a field leaves it unchanged.
- **Status transitions**: enforced only in `app/business_rules.py`, checked in the `PATCH` route handler (`app/main.py`) before `storage.update_task` runs, since it needs the task's current status.
- **Storage**: single in-memory dict (`app/storage.py`), no persistence; overdue status is computed at read time (`due_date` in the past AND `status != Done`), never stored.
- **Error handling**: `404` via `HTTPException` for missing tasks (get/patch/delete); `422` for both Pydantic validation failures and invalid status transitions.
- **Frontend/backend interaction**: frontend calls `http://localhost:8000` directly via `fetch`; backend CORS allows only `http://localhost:5500` as an origin. Board has four states (`loading`/`empty`/`error`/`ready`); the create/edit modal has its own separate inline validation-error state.

## 6. Not visible or assumptions
- Exact installed versions of FastAPI, Uvicorn, and python-dotenv are pinned in `requirements.txt` but not confirmed against the active environment (per CLAUDE.md's own [VERIFY] flags).
- Full frontend logic (drag-and-drop implementation, modal state machine) was not read in detail — only confirmed the API base URL and fetch call sites; behavior described here is CLAUDE.md-sourced.
- `docs/midcourse/` (mini-ADR, user stories, etc.) was not opened for this doc; deliberately-excluded scope items (recurring due dates, timezone-specific handling, shared tag tables) are per CLAUDE.md's summary, not independently verified.
- No database/auth/deployment config exists by design (CLAUDE.md Do-Not Rules); not something inferred from the code alone.
