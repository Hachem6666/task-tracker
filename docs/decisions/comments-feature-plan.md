# Design Doc: Comments on Tasks

**Module:** 5.4 (feature planning only — no implementation)
**Status:** Draft, read-only analysis
**Files inspected:** `app/models.py`, `app/main.py`, `app/storage.py`,
`app/business_rules.py`, `tests/test_tasks.py`, `tests/conftest.py`,
`frontend/index.html`, `CLAUDE.md`, `docs/midcourse/mini-adr.md`

## 1. Data Model

Following `app/models.py`'s existing pattern (`TaskCreate`/`TaskUpdate`/`TaskResponse`
split, `model_config = ConfigDict(extra="forbid")` on every model, `field_validator`
classmethods that `.strip()` then reject blank/overlong values — see
`validate_title` at `app/models.py:30-52` and `validate_tags` at `app/models.py:54-83`),
a comment feature would plausibly add:

- `CommentCreate`: `author: str`, `body: str`. `task_id` is not a body field — it
  comes from the URL path, mirroring how `task_id` is a path parameter on
  `GET /tasks/{task_id}` (`app/main.py:107-108`), not a body field.
- `CommentResponse`: `id: str`, `task_id: str`, `author: str`, `body: str`,
  `created_at: datetime`.
- No `CommentUpdate` model — the given spec defines no update semantics (no
  `updated_at`, no PATCH behavior requested), so the default assumption is
  comments are create-only/immutable. This mirrors nothing currently in the
  codebase; `TaskUpdate` exists because tasks are explicitly mutable.

Validators for `author` (1-100 chars) and `body` (1-2000 chars) would follow the
same trim-then-bound-check shape as `validate_title`.

### My Critique

I agree that comments should stay immutable for this design. The project requirements don't mention editing or deleting comments, and there is no updated_at field or PATCH endpoint specified for them. Keeping comments immutable makes the implementation simpler and matches the given specification. If editing or deleting comments becomes a future requirement, those features can be added later with the necessary models and endpoints.

## 2. API Routes

The existing route file (`app/main.py`) has no sub-resource routes yet — all
routes are flat under `/tasks` and `/tasks/{task_id}` (`app/main.py:54-186`).
A comments feature would most naturally add nested routes:

- `POST /tasks/{task_id}/comments` → 201, `CommentResponse`
- `GET /tasks/{task_id}/comments` → 200, `list[CommentResponse]`

Both would need the same "task not found → 404" guard already used at
`app/main.py:123-126` (`get_task_by_id`) and `app/main.py:184-186`
(`delete_task_route`) — i.e., look up the parent task first and raise
`HTTPException(404, detail=f"Task with id {task_id} not found")` before
touching the comment store.

CORS (`app/main.py:27-32`) already allows `GET` and `POST` from
`http://localhost:5500`, so no CORS config change is needed for a create+list-only
API. No auth is added, consistent with `CLAUDE.md`'s Do-Not Rules.

### My Critique

I think the nested route structure makes sense because comments belong to a specific task, so having the task ID in the path is clear and easy to understand. I also agree with reusing the existing "task not found → 404" guard since it keeps the API behavior consistent with the rest of the application. I don't see a strong reason to use a separate /comments endpoint for this project because the nested routes are simpler and better match the relationship between tasks and comments.

## 3. Tests

`tests/test_tasks.py` uses one `def test_...` function per scenario, plain
`assert` statements, the `client` fixture, and (for tests needing an existing
task) the `created_task` fixture from `tests/conftest.py:21-25`. A comments
test file would plausibly follow the same shape — e.g. a new
`tests/test_comments.py` with scenarios mirroring the existing task tests'
structure: valid creation (`test_create_task_valid_returns_201...` pattern),
missing/blank required field → 422 (`test_create_task_missing_title_returns_422`,
`test_create_task_blank_title_returns_422`), 404 on a nonexistent parent task
(`test_get_task_by_id_not_found_returns_404_with_detail`), and empty-list
behavior (`test_list_tasks_empty_returns_200_and_empty_list`).

One concrete gap: `tests/conftest.py:8-12`'s `_reset_storage` fixture only
calls `storage._reset()`, which (per `app/storage.py:149-150`) only clears
`_tasks`. If a comment store is added as a second module-level dict in
`app/storage.py`, `_reset()` would need to clear it too, or comment tests
would leak state across test runs. This is an `app/storage.py` change, so it's
out of scope to implement in this session — flagging it as a dependency.

### My Critique

I think this is a real risk and it's worth noting, even if it's a small change. If the comments storage isn't reset between tests, it could cause tests to fail unpredictably or affect each other. It's better to identify that dependency early. I also agree with creating a separate tests/test_comments.py file because it keeps the comments tests organized and follows the same structure as the existing task tests, making the project easier to maintain.

## 4. Frontend Changes

`frontend/index.html` currently has no comment UI surface at all — the only
modal is the task create/edit modal (`frontend/index.html:277-333`), and the
only UI states are the board-level `loading`/`empty`/`error`/`ready` states
managed by `setBoardState()` (`frontend/index.html:519-554`) plus the modal's
own inline `.modal__error`/`.field-error` validation state
(`frontend/index.html:192-196`, `226-230`).

Adding a comment thread would require a new UI element — most likely a
comment list + form appended inside the existing edit-task modal, since that's
the only place a single task is already in view. This is a judgment call I'm
flagging rather than assuming: `CLAUDE.md`'s Do-Not Rules say "Do not make
major UI changes (new pages, redesigns, new frameworks) without asking first."
Adding a section to an existing modal is arguably not a "new page" or
"redesign," but it is new interactive surface area, so I'd treat this as
something to confirm with you explicitly before any implementation, not
something to build by default.

### My Critique

I agree with holding off on the frontend UI decisions for now and keeping this planning pass focused on the API. While adding comments to the existing edit-task modal seems like a reasonable approach, it's still a UI change that should be confirmed before committing to it. I think it's better to keep the frontend as a follow-up task after the API is complete and the overall approach has been confirmed.

## 5. Migration or Storage Notes

There is no database and no migration tooling in this repo — `app/storage.py`
is a single module-level dict, `_tasks: dict[str, TaskResponse] = {}`
(`app/storage.py:6`), with CRUD functions operating directly on it and a
`_reset()` for test isolation (`app/storage.py:149-150`). A comments feature
would plausibly add a second module-level store, e.g.
`_comments: dict[str, CommentResponse] = {}`, with a list/filter function
scoped by `task_id` — structurally similar to the existing `tag=` filter in
`get_all_tasks` (`app/storage.py:80-82`), but filtering by exact `task_id`
match instead of substring/case-insensitive tag match.

One decision this repo has no precedent for: `delete_task`
(`app/storage.py:133-146`) currently deletes a task with no cascade logic,
because no related child data exists yet. Whether deleting a task should
cascade-delete its comments is a new decision, not something inferable from
existing code.

### My Critique

I think deleting a task should also delete its comments. Since comments only exist as part of a task, there isn't much value in keeping them after the task is gone. Cascade deletion keeps the data clean and avoids orphaned comments. I also think using a second module-level _comments dictionary is a reasonable approach because it matches the existing storage design and keeps the implementation simple and consistent for this project.

## 6. Open Questions

- Are comments mutable (edit/delete) after creation, or strictly append-only?
  The given field spec has no `updated_at` and defines no update endpoint,
  which suggests append-only, but this isn't stated explicitly.
- Does deleting a task cascade-delete its comments, block deletion if comments
  exist, or leave orphaned comments? No existing code establishes a precedent.
- Should `GET /tasks/{task_id}` (`app/main.py:107-126`) embed comments inline,
  or stay comment-agnostic with a separate `GET /tasks/{task_id}/comments`
  call? Embedding would require adding a field to `TaskResponse`
  (`app/models.py:166-178`), which currently has `extra="forbid"` and a fixed
  field set — not a small change.
- What order should `GET /tasks/{task_id}/comments` return comments in?
  Chronological ascending by `created_at` is the likely default but isn't
  specified.
- Is frontend UI for comments in scope now, or is this planning pass API-only
  for a later module? (Related to the Do-Not Rule flagged in Section 4.)
- Should this feature get its own mini-ADR entry in `docs/midcourse/mini-adr.md`
  (matching the format of the two existing entries, `docs/midcourse/mini-adr.md:1-21`)
  once scope is decided, the way due dates and tags each did?

## Generic vs. Repo-Grounded Comparison

**Biggest difference:**
The biggest difference was that the repo-grounded plan matched the existing project structure and coding patterns, while the generic plan was more of a high-level design. The repo-grounded version identified dependencies, such as updating the test reset fixture, that the generic plan couldn't know about.

**Plan I would hand to a teammate:**
I would hand the repo-grounded plan to a teammate because it fits the current codebase, follows the existing API and testing patterns, and would be easier to implement without introducing inconsistencies.

**Where the generic plan was still useful:**
The generic plan was still useful because it provided a good overview of how the comments feature could be designed. It helped identify the main components and API requirements before adapting the solution to the actual repository.
