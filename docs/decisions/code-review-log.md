# Code Review Log: R1 Diff Review + Triage (Module 4 CI/Docker)

Source: AI code review (R1) of `git diff master...mid-course-project`, followed by manual triage in conversation.

| Comment summary | Bucket | Evidence | Action taken |
|---|---|---|---|
| CLAUDE.md's Notes section documents the PATCH null-`title` rejection but has no matching bullet for null-`tags`, even though `app/models.py`'s `TaskUpdate.validate_tags` now rejects it identically | Useful | `CLAUDE.md` Notes had one bullet for title, none for tags; `app/models.py` (same diff) shows both validators raise on `None` the same way | Added a "PATCH null-tags rule" bullet to `CLAUDE.md`'s Notes section (commit `b40b7a3`) |
| The branch mixes two unrelated bug fixes (naive-datetime overdue comparison, PATCH null-title/tags rejection) into the same diff as the Module 4 CI/Docker/docstring work | Noise | Diff does mix these, but each fix has its own commit and this is a single-branch course project, not a multi-team PR pipeline — a process observation, not a defect | None |
| The `docker-verify` health-check loop only retries for 10 seconds before failing the job, which could flake on a slower runner | Noise | Originally flagged "Needs manual check." Resolved: no flakes observed across multiple real CI runs this session (health check passed on first attempt each time), but the window also hasn't been stress-tested under load — absence of an observed problem is treated as not-actionable-now rather than a confirmed risk | None |
| `Dockerfile` hardcodes `python:3.11-slim` independently in both the builder and runtime `FROM` lines | Noise | Two literal `FROM python:3.11-slim` lines confirmed in the file, but it's a 25-line Dockerfile edited by hand — an `ARG` for a single duplicated pin is more abstraction than the file's size/change frequency justifies | None |
