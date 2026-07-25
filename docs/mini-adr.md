# Mid-Course Project — Mini ADR

## Feature 1: Due dates + overdue filter

**Decision:** Add an optional `due_date` field (ISO 8601 datetime string) to `TaskCreate` and `TaskUpdate`. Overdue status is computed on read (in the backend), not stored — a task is "overdue" if `due_date` is in the past AND `status != Done`. Added an optional `overdue=true` query parameter on `GET /tasks`.

**Alternatives considered:**
- Computing overdue status in the frontend instead of the backend — rejected, since the backend is the single source of truth and the frontend would need to duplicate the "not Done" exception logic.
- Storing a persistent `is_overdue` boolean, updated on a schedule — rejected as unnecessary complexity for this project's scope; computing it live on each read is simpler and always accurate.

**Rejected as out of scope:** Recurring due dates, reminders/notifications, timezone-specific due date handling beyond basic ISO 8601 parsing.

## Feature 2: Tags / labels

**Decision:** Add an optional `tags` field (list of strings) to `TaskCreate` and `TaskUpdate`, defaulting to an empty list. Each tag is trimmed and validated as non-empty; a maximum of 10 tags per task and 30 characters per tag are enforced. Added an optional `tag=` query parameter on `GET /tasks` for case-insensitive filtering.

**Alternatives considered:**
- Comma-separated string field instead of a list — rejected, since a list is easier to validate per-tag and avoids ambiguous parsing (e.g. tags containing commas).
- Free-form tag limits (no cap) — rejected in favor of a small sane limit (10 tags, 30 chars) to prevent obviously abusive input without adding real complexity.

**Rejected as out of scope:** A separate tags/labels management table (e.g. shared tag list across tasks with autocomplete), tag color coding, tag-based permissions.