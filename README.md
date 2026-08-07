# Task Tracker

A FastAPI backend and vanilla JS frontend for tracking tasks on a Kanban-style board, built across Modules 1-3, extended in the Mid-Course Project with due dates/overdue filtering and tags, and given a CI workflow and a local Dockerfile in Module 4. Supports full task CRUD, status transitions, drag-and-drop, and a create/edit modal.

This is a course project. It is **not** deployed anywhere, has **no** authentication, and stores data **in memory only** (see [Project Conventions and Current Limitations](#9-project-conventions-and-current-limitations)).

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Prerequisites](#2-prerequisites)
3. [Local Setup](#3-local-setup)
4. [Run the App Locally](#4-run-the-app-locally)
5. [Run Tests](#5-run-tests)
6. [Run with Docker](#6-run-with-docker)
7. [CI Workflow Summary](#7-ci-workflow-summary)
8. [Project Structure](#8-project-structure)
9. [Project Conventions and Current Limitations](#9-project-conventions-and-current-limitations)
10. [Design Decisions / Further Docs](#10-design-decisions--further-docs)

## 1. Project Overview

The backend (`app/`) is a FastAPI service exposing `/health` and full CRUD on `/tasks`, with status-transition rules, due-date/overdue filtering, and tags. The frontend (`frontend/index.html`) is a single-file vanilla JS Kanban board (drag-and-drop, create/edit modal) that talks to the backend over `fetch`. There is no database — tasks live in an in-memory dict and reset whenever the server restarts.

## 2. Prerequisites

- Python 3.11 or newer
- `pip`
- Git
- Docker Desktop or Docker Engine — optional, only needed for [Run with Docker](#6-run-with-docker) [VERIFY exact Docker version required — not pinned in this repo]

## 3. Local Setup

All commands below are run from the repository root.

1. Create and activate a virtual environment:

   **macOS / Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   **Windows (PowerShell):**
   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   This installs FastAPI, Uvicorn, Pydantic, python-dotenv, httpx, and pytest — see [`requirements.txt`](requirements.txt). [VERIFY installed versions exactly match the pins in requirements.txt in your environment]

3. Copy the example environment file:

   **macOS / Linux:**
   ```bash
   cp .env.example .env
   ```

   **Windows (PowerShell):**
   ```powershell
   copy .env.example .env
   ```

## 4. Run the App Locally

### Backend

From the repository root, with your virtual environment activated:

```bash
uvicorn app.main:app --reload --port 8000
```

The API runs at `http://127.0.0.1:8000`. Interactive Swagger docs: `http://127.0.0.1:8000/docs`.

Verify it's up:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{"status": "ok", "timestamp": "2026-07-12T12:00:00.000000+00:00"}
```

### Frontend

In a separate terminal, from the repository root, with the backend already running:

```bash
python -m http.server 5500 --directory frontend
```

Then open in your browser: `http://localhost:5500/index.html`

The frontend **must** be served from `http://localhost:5500` — the backend's CORS policy (`app/main.py`) only allows that exact origin.

### Features

- **Due dates + overdue filter:** Set an optional due date when creating or editing a task. Tasks with a past due date (and not marked "Done") show a red "Overdue" badge on their card. Filter via `GET /tasks?overdue=true`.
- **Tags:** Add comma-separated tags when creating or editing a task. Tags display as chips on each card. Filter via `GET /tasks?tag=<tag_name>` (case-insensitive).

## 5. Run Tests

From the repository root, with your virtual environment activated:

```bash
pytest -v
```

All 27 tests should pass (CRUD, status transitions, filters, due dates, tags, and PATCH null-field regression tests).

## 6. Run with Docker

Local build-and-run only — this does **not** push to a registry, deploy anywhere, or add orchestration. See [`Dockerfile`](Dockerfile) and [`.dockerignore`](.dockerignore).

From the repository root:

```bash
docker build -t task-tracker:dev .
docker run -d --name task-tracker-dev -p 8000:8000 task-tracker:dev
curl http://localhost:8000/health
```

The image is a multi-stage build on `python:3.11-slim`, runs as a non-root user (`app`), and does not use `--reload`.

Stop and remove the container when done:

```bash
docker stop task-tracker-dev && docker rm task-tracker-dev
```

The frontend is not containerized; run it separately per [Run the App Locally](#4-run-the-app-locally) if needed alongside the containerized backend.

## 7. CI Workflow Summary

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every `push` and `pull_request`, with two jobs:

- **`test`** — checks out the repo, sets up Python 3.11, installs `requirements.txt`, and runs `pytest -v`.
- **`docker-verify`** — builds the image from the `Dockerfile`, starts a container mapping port 8000, polls `GET /health` until it returns 200 (failing the job if it never does), asserts the container's runtime user is `app` via `docker exec ... whoami`, then stops and removes the container.

Neither job pushes an image to a registry, logs into anything, or deploys. [VERIFY both jobs pass on an actual GitHub Actions run — reviewed the workflow definition but haven't observed a live run's result]

## 8. Project Structure

```bash
task-tracker/
├── app/
│   ├── main.py            # FastAPI app, CORS, route handlers
│   ├── models.py           # Pydantic models + field validators
│   ├── business_rules.py   # Status-transition rules
│   └── storage.py          # In-memory store + filtering
├── frontend/
│   └── index.html          # Single-file vanilla JS Kanban board
├── tests/
│   ├── conftest.py         # pytest fixtures (client, created_task, _reset_storage)
│   ├── test_tasks.py       # Main pytest suite
│   └── verify_a.py         # Standalone script, not pytest-discovered
├── docs/
│   └── midcourse/          # User stories, mini-ADR, prompt log, verification, reflection
├── .github/
│   └── workflows/
│       └── ci.yml          # test + docker-verify jobs
├── Dockerfile               # Multi-stage build, local build/run only
├── .dockerignore
├── requirements.txt
├── .env.example
├── CLAUDE.md                # Detailed project conventions for AI-assisted work
└── README.md
```

## 9. Project Conventions and Current Limitations

- **No auth/authorization.** Anyone who can reach the API can use it.
- **No database.** Tasks are stored in an in-memory `dict` (`app/storage.py`); all data is lost on server restart. There is no persistence layer.
- **No deployment.** This module is local-only: no hosting, no orchestration (docker-compose/Kubernetes), no registry push. The Dockerfile and CI exist for local/CI verification, not for shipping the app anywhere.
- **Status transitions are restricted:** `ToDo → InProgress`, `InProgress → Done`, `Done → InProgress` only. Any other transition, including same-status (e.g. `ToDo → ToDo`), is rejected with `422`. See `app/business_rules.py`.
- **PATCH rejects explicit `null` for `title` and `tags`:** `{"title": null}` or `{"tags": null}` on `PATCH /tasks/{task_id}` returns `422`. Omitting either field from the PATCH body leaves it unchanged. See `app/models.py`.
- **Overdue is computed, not stored:** a task is overdue if `due_date` is in the past and `status != Done`, recalculated on every read (`app/storage.py`).
- **CORS is locked to `http://localhost:5500`.** The frontend must be served from exactly that origin, or the browser will block requests.
- **Tags are case-insensitive on filter, case-preserving on storage:** `GET /tasks?tag=Urgent` matches a stored tag `"urgent"`, but the tag itself isn't lowercased when saved.

## 10. Design Decisions / Further Docs

See [`docs/midcourse/`](docs/midcourse/) for:

- [`mini-adr.md`](docs/midcourse/mini-adr.md) — design decisions, alternatives considered, and scope deliberately left out (recurring due dates, timezone-specific handling, shared tag tables, etc.)
- [`user-stories.md`](docs/midcourse/user-stories.md)
- [`prompt-log.md`](docs/midcourse/prompt-log.md)
- [`verification.md`](docs/midcourse/verification.md)
- [`reflection.md`](docs/midcourse/reflection.md)
- [`docs/decisions/ci-workflow-design.md`](docs/decisions/ci-workflow-design.md) — technical decision note on the Module 4 CI workflow design (context, alternatives considered, trade-offs, and open questions).
- [`docs/decisions/code-review-log.md`](docs/decisions/code-review-log.md) — AI code review comments for the Module 4 diff, triaged into Useful/Noise/Wrong with evidence and actions taken.
- [`docs/decisions/module4-reflection.md`](docs/decisions/module4-reflection.md) — reflection on AI tools used during Module 4 (GitHub Copilot, Claude Code, Cursor/Codex).

See also [`CLAUDE.md`](CLAUDE.md) for the fuller technical reference (tech stack, architecture, business rules, and do-not rules) used to guide AI-assisted work on this repo.
## Final Project

Branch reviewed: final-project

### What this submission demonstrates
- Existing Task Tracker app still runs inside the intended course scope.
- CI runs the pytest suite on push and/or pull request.
- Docker image builds and runs with /health returning 200.
- AI review, security, and ownership evidence is in docs/.

### How to run locally
```bash
uvicorn app.main:app --reload --port 8000
```
(in a separate terminal, from the repository root)
```bash
python -m http.server 5500 --directory frontend
```
Then open `http://localhost:5500/index.html`.

### How to run tests
```bash
pytest -v
```

### How to run with Docker
```bash
docker build -t task-tracker:dev .
docker run -d --name task-tracker-dev -p 8000:8000 task-tracker:dev
curl http://localhost:8000/health
```

### Evidence files
- docs/release-evidence.md
- docs/final-ai-review.md
- docs/ai-playbook.md

### AI assistance summary
AI helped draft or review: CI workflow, Docker setup, security review, feature planning, context-engineering comparison, and documentation.
I verified the work by: running the full pytest suite, checking `/health` directly, visually confirming the frontend board, and comparing AI claims against actual repo files and commits before accepting them.
One AI suggestion I rejected or corrected: during Module 5.5's context-engineering exercise, Claude Code initially cited claims from `CLAUDE.md` without disclosing that the content was auto-injected rather than independently read — I challenged this twice (Strategy A and Strategy C) and required it to correct its Files Inspected list before I accepted the drafts.