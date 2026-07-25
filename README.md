# Task Tracker API — Module 1 Skeleton

A minimal FastAPI skeleton for the Task Tracker learning project. This skeleton
only includes a `/health` endpoint to verify the server runs correctly. Task
CRUD features are added in later steps of the module.

## Requirements

- Python 3.11 or newer

## Setup

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

3. Copy the example environment file:

   **macOS / Linux:**
```bash
   cp .env.example .env
```

   **Windows (PowerShell):**
```powershell
   copy .env.example .env
```

## Run the server

```bash
uvicorn app.main:app --reload
```

The server starts at `http://127.0.0.1:8000` by default.

## Test the health endpoint

```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{"status": "ok", "timestamp": "2026-07-12T12:00:00.000000+00:00"}
```

## View interactive API docs (Swagger)

Open this URL in your browser while the server is running:
http://127.0.0.1:8000/docs

## Mid-Course Project — Running the Full App

This adds a frontend and two new features (due dates + overdue filter, tags + tag filter) on top of the Module 1-3 backend.

### 1. Run the backend

From the project root, with your virtual environment activated:

```bash
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`.

### 2. Open the frontend

In a separate terminal, from the project root:

```bash
python -m http.server 5500 --directory frontend
```

Then open in your browser:
 http://localhost:5500/index.html

### 3. Run the tests

From the project root, with your virtual environment activated:

```bash
pytest tests/test_tasks.py -v
```

All 24 tests (18 original + 6 covering due dates, tags, and their filters) should pass.

### New features

- **Due dates + overdue filter:** Set an optional due date when creating or editing a task. Tasks with a past due date (and not marked "Done") show a red "Overdue" badge on their card. Filter via `GET /tasks?overdue=true`.
- **Tags:** Add comma-separated tags when creating or editing a task. Tags display as chips on each card. Filter via `GET /tasks?tag=<tag_name>` (case-insensitive).

See `docs/midcourse/` for user stories, the design decision log (mini-ADR), prompt log, verification evidence, and project reflection.