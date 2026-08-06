# Task Tracker — Architecture

## 1. What the App Does
Task Tracker is a small full-stack Kanban-style task manager: a FastAPI backend exposes CRUD endpoints for tasks (with status transitions, due dates, priorities, and tags), and a single-file vanilla-JS frontend renders them as a drag-and-drop board. There is no database or authentication — tasks live in memory for the lifetime of the server process.

## 2. Data Model
A **Task** (`TaskResponse` in `app/models.py`) has:
- `id` (str, UUID4, server-generated)
- `title` (str, required, 1–200 chars, trimmed)
- `description` (str, optional, default `""`)
- `status` (enum: `ToDo` | `InProgress` | `Done`, default `ToDo`)
- `priority` (enum: `Low` | `Medium` | `High`, default `Medium`)
- `assignee` (str, optional)
- `due_date` (datetime, optional; naive values are treated as UTC)
- `tags` (list[str], ≤10 tags, each ≤30 chars, trimmed)
- `created_at`, `updated_at` (datetime, server-set)

Separate `TaskCreate` and `TaskUpdate` models govern input: `TaskUpdate` fields are all optional (partial update / PATCH semantics), but an explicitly-null `title` or `tags` is rejected rather than treated as "no change."

## 3. Request Flow — Creating a Task
1. Frontend `fetch(POST /tasks)` sends a JSON body (title required; other fields optional) to `http://localhost:8000`.
2. FastAPI routes to `create_task` in `app/main.py`, which parses/validates the body into a `TaskCreate` model (Pydantic field validators trim/check `title` and `tags`; unknown fields are rejected via `extra="forbid"`).
3. `storage.add_task()` generates a UUID `id`, stamps `created_at`/`updated_at` to now (UTC), stores the resulting `TaskResponse` in the module-level `_tasks` dict, and returns it.
4. FastAPI serializes the `TaskResponse` back as JSON with `201 Created`.
5. Frontend re-fetches/updates the board state (`loading` → `ready`) and renders the new card; validation failures surface as `422` and are shown inline in the modal.

## 4. Key Files
- `app/main.py` — FastAPI app, CORS config, and all HTTP routes (`/health`, `/tasks`, `/tasks/{id}`).
- `app/models.py` — Pydantic request/response models and field-level validation (title, tags).
- `app/business_rules.py` — `VALID_TRANSITIONS` and `validate_status_transition()`, the sole source of status-transition rules.
- `app/storage.py` — in-memory `_tasks` store, plus filtering (status/priority/overdue/tag) and overdue computation.
- `frontend/index.html` — single-file vanilla-JS UI: board rendering, drag-and-drop, create/edit modal, fetch calls to the API.
- `tests/test_tasks.py` — pytest suite covering CRUD, transitions, filters, due dates, tags.
- `tests/conftest.py` — shared fixtures, including autouse in-memory store reset between tests.
- `requirements.txt` — pinned dependencies (FastAPI 0.110.0, Pydantic ≥2.9.2, Uvicorn 0.29.0, pytest 8.4.2, python-dotenv 1.0.1, httpx<0.28).
- `Dockerfile` — local-only container build (no orchestration/registry config).

## 5. Conventions
- **Validation**: field-level rules (title/tag trimming, length, count) live in `app/models.py` via Pydantic `field_validator`s and run on every create/update. Both `TaskCreate` and `TaskUpdate` use `extra="forbid"`, so unknown JSON keys are rejected.
- **Business rules**: status transitions are validated separately in `app/main.py`'s PATCH handler (via `business_rules.validate_status_transition`) *before* calling storage, because it needs the task's current status. Invalid transitions (including same→same) raise `422` with the allowed-transitions list in the error detail.
- **Storage**: a single process-global dict (`app/storage._tasks`), no persistence — data is lost on restart. Filtering (status, priority, tag, overdue) and overdue computation happen at read time, not stored as flags; overdue = `due_date` in the past AND `status != Done`.
- **Error handling**: not-found lookups raise `HTTPException(404)` in the route handlers; validation failures surface as FastAPI/Pydantic `422` responses automatically.
- **Frontend/backend interaction**: the frontend calls a hardcoded `API_BASE_URL = "http://localhost:8000"` via `fetch`; CORS on the backend only allows origin `http://localhost:5500`, so the frontend must be served from that exact origin. The board tracks explicit UI states (`loading`, `empty`, `error`, `ready`) separate from the modal's own inline validation-error state.

## 6. Not Visible / Assumptions
- Exact installed versions of FastAPI, Uvicorn, and python-dotenv are pinned in `requirements.txt` but not verified against the active environment (flagged as such in `CLAUDE.md`).
- `frontend/index.html` was sampled (fetch calls, state function, API base URL) rather than read in full; finer UI/rendering details are not covered here.
- No `.env` file was inspected — `APP_ENV`/`PORT` behavior is inferred from `app/main.py`'s `load_dotenv()` call only.
- `docs/midcourse/` (user stories, mini-ADR, scope decisions) exists but was not consulted for this doc; some "why" behind due-date/tag scope limits is therefore not reflected here.
- No authentication, database, or deployment config exists by design (see `CLAUDE.md` Do-Not Rules) — this is a local-only, in-memory app.
