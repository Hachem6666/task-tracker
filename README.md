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

```
http://127.0.0.1:8000/docs
```
