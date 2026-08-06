# Task Tracker — Architecture

## 1. What the App Does
Task Tracker is a small full-stack Kanban-style task manager: a FastAPI backend exposes CRUD endpoints for tasks (with status transitions, due dates, priorities, and tags), and a single-file vanilla-JS frontend renders them as a drag-and-drop board across ToDo / InProgress / Done columns. There is no database or authentication — tasks live in memory for the lifetime of the server process.

## 2. Data Model
Core entity: **Task** (`TaskResponse` in `app/models.py`):
- `id` (str, UUID4, server-generated)
- `title` (str, required, 1–200 chars, trimmed)
- `description` (str, optional, default `""`)
- `status` — **TaskStatus** enum: `ToDo` | `InProgress` | `Done` (default `ToDo`)
- `priority` — **TaskPriority** enum: `Low` | `Medium` | `High` (default `Medium`)
- `assignee` (str, optional)
- `due_date` (datetime, optional; naive values are treated as UTC)
- `tags` (list[str], max 10, each 1–30 chars, trimmed)
- `created_at`, `updated_at` (datetime, server-set, UTC)

Separate input models govern requests:
- **TaskCreate** (POST): same fields as above (minus `id`/timestamps), with `title` required. `extra="forbid"` rejects unknown JSON keys.
- **TaskUpdate** (PATCH): all fields optional for partial updates, also `extra="forbid"`. An explicitly-null `title` or `tags` is rejected rather than treated as "no change"; omitting a field leaves it unchanged.
- **TaskResponse**: the stored/returned shape — `id`, `title`, `description`, `status`, `priority`, `assignee`, `created_at`, `updated_at`, `due_date`, `tags`.

## 3. Request Flow — Creating a Task
1. Frontend `fetch(POST /tasks)` sends a JSON body (title required; other fields optional) to `API_BASE_URL = http://localhost:8000`.
2. FastAPI routes to `create_task` in `app/main.py`, which parses/validates the body into a `TaskCreate` model — Pydantic `field_validator`s trim/check `title` and `tags`; unknown fields are rejected via `extra="forbid"`. Failure → `422` before the route body runs.
3. `create_task()` calls `storage.add_task(payload)`, which generates a UUID `id`, stamps `created_at`/`updated_at` to `datetime.now(timezone.utc)`, builds the `TaskResponse`, and stores it in the module-level `_tasks` dict keyed by id.
4. FastAPI serializes the `TaskResponse` back as JSON with `201 Created`.
5. Frontend re-fetches/updates the board state (`loading` → `ready`) and renders the new card; validation failures surface as `422` and are shown inline in the modal.

## 4. Key Files
- `app/main.py` — FastAPI app instance, CORS config, and all HTTP routes (`/health`, `/tasks` GET/POST, `/tasks/{id}` GET/PATCH/DELETE).
- `app/models.py` — Pydantic v2 request/response models (`TaskCreate`, `TaskUpdate`, `TaskResponse`, `TaskStatus`, `TaskPriority`) and field-level validation (title, tags).
- `app/business_rules.py` — `VALID_TRANSITIONS` and `validate_status_transition()`, the sole source of status-transition rules.
- `app/storage.py` — in-memory `_tasks` dict; CRUD plus read-time filtering (status, priority, overdue, tag) and naive→UTC datetime normalization (`_as_aware_utc`).
- `frontend/index.html` — single-file vanilla-JS Kanban UI: board rendering, drag-and-drop, create/edit modal, fetch calls to the API.
- `tests/test_tasks.py` — pytest suite covering CRUD, transitions, filters, due dates, tags.
- `tests/conftest.py` — shared fixtures (`client`, `created_task`), including autouse in-memory store reset between tests.
- `requirements.txt` — pinned dependencies (FastAPI 0.110.0, Pydantic ≥2.9.2, Uvicorn 0.29.0, pytest 8.4.2, python-dotenv 1.0.1, httpx<0.28).
- `Dockerfile` — local-only container build (no orchestration/registry config).

## 5. Conventions
- **Validation**: field-level rules (title/tag trimming, length, count) live in `app/models.py` via Pydantic `field_validator`s and run on every create/update. Both `TaskCreate` and `TaskUpdate` use `extra="forbid"`, so unknown JSON keys are rejected. `TaskUpdate` additionally rejects explicit `null` for `title`/`tags`, while omitting a field leaves it unchanged.
- **Status transitions**: validated separately in `app/main.py`'s PATCH handler — it checks `payload.status is not None`, fetches the existing task, and calls `business_rules.validate_status_transition(existing_task.status, payload.status)` *before* calling `storage.update_task`, because it needs the task's current status. Invalid transitions (including same→same) raise `422` with the allowed-transitions list in the error detail.
- **Partial updates**: `storage.update_task` uses `payload.model_dump(exclude_unset=True)` so only explicitly-provided fields are applied via `setattr`; omitted fields are left unchanged. Values are not re-validated against `TaskResponse` at this point — it relies on `TaskUpdate`'s own validators instead.
- **Storage**: a single process-global dict (`app/storage._tasks`), no persistence — data is lost on restart. Filtering (status, priority, tag, overdue) and overdue computation happen at read time, not stored as flags; overdue = `due_date` in the past AND `status != Done`.
- **Error handling**: not-found lookups raise `HTTPException(404)` in the route handlers (GET/PATCH/DELETE by id); validation failures (Pydantic and invalid status transitions) surface as `422` responses.
- **Frontend/backend interaction**: the frontend calls a hardcoded `API_BASE_URL = "http://localhost:8000"` via `fetch`; CORS on the backend only allows origin `http://localhost:5500` (methods `GET, POST, PATCH, DELETE, OPTIONS`, all headers), so the frontend must be served from that exact origin. The board tracks explicit UI states (`loading`, `empty`, `error`, `ready`) separate from the modal's own inline validation-error state.

## 6. Not Visible / Assumptions
- Exact installed versions of FastAPI, Uvicorn, and python-dotenv are pinned in `requirements.txt` but not verified against the active environment.
- `frontend/index.html` was sampled (fetch calls, state function, API base URL) rather than read in full; finer UI/rendering details (drag-and-drop implementation, modal state machine) are not covered here.
- No `.env` file was inspected — `APP_ENV`/`PORT` behavior is inferred from `app/main.py`'s `load_dotenv()`/`os.getenv` calls only.
- `docs/midcourse/` (user stories, mini-ADR, scope decisions) exists but was not consulted for this doc; the "why" behind due-date/tag scope limits (e.g. recurring due dates, timezone-specific handling, shared tag tables being out of scope) is therefore not reflected here.
- No authentication, database, or deployment config exists by design — this is a local-only, in-memory app.

## Context Strategy Comparison
### Strategy A
- What it got right:
- What it got wrong, invented, or missed:
### Strategy B
- What it got right:
- What it got wrong, invented, or missed:
### Strategy C
- What it got right:
- What it got wrong, invented, or missed:
### Verdict
I picked Strategy ___ because ___
