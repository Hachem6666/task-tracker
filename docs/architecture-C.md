# Task Tracker — Architecture (Strategy C: Targeted Context)

*Source: app/main.py, app/models.py, app/storage.py only.*

## 1. What the app does
A backend API for tracking tasks: create, list (with filters), retrieve,
partially update, and delete tasks. Each task has a title, description,
status, priority, optional assignee, optional due date, and tags.

## 2. Data model
- **TaskStatus** (enum): `ToDo`, `InProgress`, `Done`.
- **TaskPriority** (enum): `Low`, `Medium`, `High`.
- **TaskCreate**: `title` (required, stripped, 1–200 chars), `description`
  (default `""`), `status` (default `ToDo`), `priority` (default `Medium`),
  `assignee` (optional), `due_date` (optional datetime), `tags` (list, max
  10, each stripped, 1–30 chars). `extra="forbid"`.
- **TaskUpdate**: same fields, all optional, but explicit `null` is
  rejected for `title` and `tags` specifically (validators raise on
  `None`). `extra="forbid"`.
- **TaskResponse**: `id`, `title`, `description`, `status`, `priority`,
  `assignee`, `created_at`, `updated_at`, `due_date`, `tags`. This is the
  stored/returned shape.

## 3. Request flow — creating a task
1. Client sends `POST /tasks` with a JSON body.
2. FastAPI parses/validates it into `TaskCreate`; Pydantic runs
   `validate_title` and `validate_tags` field validators.
3. Route handler `create_task` (app/main.py) calls `storage.add_task(payload)`.
4. `add_task` generates a UUID `id`, sets `created_at`/`updated_at` to the
   current UTC time, builds a `TaskResponse`, and stores it in the
   module-level `_tasks` dict keyed by id.
5. The `TaskResponse` is returned with HTTP 201.

## 4. Key files
- `app/main.py` — FastAPI app, CORS config, all HTTP routes.
- `app/models.py` — Pydantic schemas (`TaskCreate`, `TaskUpdate`,
  `TaskResponse`) and field-level validation for title/tags.
- `app/storage.py` — in-memory `_tasks` dict; CRUD + filtering functions;
  UTC-awareness helper `_as_aware_utc`.
- `app/business_rules.py` — imported by main.py as `validate_status_transition`;
  not read, so not visible from the files I read.

## 5. Conventions
- **Validation**: enforced by Pydantic field validators in `models.py`
  (title trim + 1–200 chars; tags trim + 1–30 chars, max 10). `extra="forbid"`
  on all three models rejects unknown fields.
- **Storage**: purely in-memory (`dict[str, TaskResponse]` in `storage.py`),
  no persistence layer visible.
- **Partial updates**: `update_task` uses `payload.model_dump(exclude_unset=True)`
  so only explicitly-provided fields are applied via `setattr`; omitted
  fields are left unchanged. Values are not re-validated against
  `TaskResponse` at this point (comment notes `TaskResponse` doesn't enable
  `validate_assignment`, relying on `TaskUpdate`'s own validators instead).
- **Status transitions**: `main.py`'s `update_task_route` checks
  `payload.status is not None`, fetches the existing task, and calls
  `validate_status_transition(existing_task.status, payload.status)`
  before calling `storage.update_task`. The actual transition rules are in
  `business_rules.py`, which I did not read.
- **Error handling**: `HTTPException(404)` for missing tasks on GET/PATCH/DELETE
  by id; Pydantic validation failures surface as FastAPI's automatic 422
  responses.
- **Overdue filtering**: computed at read time in `get_all_tasks` (not
  stored) — `due_date < now` and `status != Done`; naive datetimes are
  normalized to UTC via `_as_aware_utc` before comparison.
- **Frontend/backend interaction**: CORS middleware in `main.py` allows only
  `http://localhost:5500` as origin, with `GET, POST, PATCH, DELETE, OPTIONS`
  and all headers. No frontend code was read, so how it actually calls the
  API is not visible from the files I read.

## 6. Not visible / assumptions
- Contents of `app/business_rules.py` (the actual `VALID_TRANSITIONS` set) —
  not visible from the files I read; only its import and call site are.
- Frontend implementation — not visible from the files I read.
- Test suite / behavior verification — not visible from the files I read.
- Whether installed package versions match `requirements.txt` pins — not
  visible from the files I read.
- Any `.env` values (`PORT`, `APP_ENV` usage beyond the `os.getenv` call) —
  not visible from the files I read.

## 7. What this targeted strategy likely missed
- **`app/business_rules.py`** — excluded by the file list, but directly
  referenced by `main.py` for status-transition validation. Without it,
  the actual `VALID_TRANSITIONS` rules (e.g. which transitions are legal)
  are unknown, even though the *mechanism* that calls them is visible.
- **`frontend/index.html`** — CORS config hints at a frontend on port 5500,
  but its UI states, request patterns, and error handling are invisible.
- **`tests/`** — no confirmation that documented behavior (e.g. overdue
  filtering, null-tag rejection) is actually exercised or correct in
  practice.
- **`docs/midcourse/`** (mini-ADR) — not consulted by this targeted read.
  *(Note, sourced from auto-injected CLAUDE.md context, not from the three
  files read: CLAUDE.md states this doc records decisions like recurring
  due dates and timezone handling as deliberately out-of-scope — meaning
  the doc above may look like it's missing "obvious" features that were in
  fact intentionally excluded. This claim is flagged separately since it
  did not come from app/main.py, app/models.py, or app/storage.py.)*
- **`requirements.txt` / `.env`** — version pins and environment config not
  verified against files read.
