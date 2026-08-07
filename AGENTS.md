# AGENTS.md

This file provides repository-level guidance for any AI coding tool working in this repository (Cursor, GitHub Copilot, Codex App, Claude Code, or general-purpose chat with repo access).

**Note on CLAUDE.md**: this repository also contains `CLAUDE.md`, which Claude Code reads automatically as project instructions. Its content is consolidated here; `CLAUDE.md` is kept as-is for tool compatibility, since removing it would change Claude Code's automatic context-loading behavior. Treat this file as authoritative.

## 1. Tech Stack

- Python 3.11+

- FastAPI 0.110.0

- Pydantic v2 (`pydantic>=2.9.2`)

- Uvicorn 0.29.0

- pytest 8.4.2

- httpx<0.28

- python-dotenv 1.0.1

- Vanilla JavaScript frontend (`frontend/index.html`) — single file, no framework, no build step

## 2. Run Command

```bash

uvicorn app.main:app --reload --port 8000

```

## 3. Test Command

```bash

pytest -v

```

## 4. Guardrails

- **Read-first, docs-first by default.** Prefer read-only analysis. Treat `docs/` as the default working area for planning, review, and governance tasks.

- **No changes to `app/` or `frontend/` without explicit approval.** Only touch these directories for a specific, requested bug fix, security fix, or documentation-supported correction — and explain any such change in `docs/final-ai-review.md`.

- **One bounded task per session.** Avoid mixing unrelated changes in a single working session.

- **Cite real files.** When making claims about this repository, cite the actual files inspected. If a file was not read, say so rather than inferring from framework convention.

- **No real secrets or personal data.** Never paste credentials, `.env` values, tokens, production logs, or real personal/customer data into an AI tool or into this repository.

## 5. Project Rules (Do-Not Rules)

- Do not add authentication/authorization.

- Do not add a database or persistence layer.

- Do not add deployment steps or config (hosting, orchestration, CI/CD publishing).

- CI is test-only (`pytest -v` on push/PR). Do not add deployment or publishing steps without asking first.

- A local build/run Dockerfile and `.dockerignore` are permitted. Do not add orchestration (docker-compose, Kubernetes), a registry push, or hosting config without asking first.

- Do not make major UI changes (new pages, redesigns, new frameworks) without asking first.

- Do not add new product features (comments, notifications, etc.) as part of release-hardening or documentation work.

## 6. Architecture Summary

- `app/main.py` — FastAPI app instance, CORS middleware, all routes.

- `app/models.py` — Pydantic models and field-level validation.

- `app/business_rules.py` — status-transition rules (`VALID_TRANSITIONS`, `validate_status_transition()`).

- `app/storage.py` — in-memory store, no database, filtering logic (status, priority, overdue, tag).

- `frontend/index.html` — single-file vanilla JS Kanban board.

- `tests/` — pytest suite (`test_tasks.py`), fixtures (`conftest.py`).

See `CLAUDE.md` for additional implementation-level detail (business rule specifics, UI state names, datetime-handling notes).
