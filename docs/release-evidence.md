# Release Evidence

## Baseline
- Branch: final-project
- Date: 2026-08-07
- Local app run command: `uvicorn app.main:app --reload --port 8000`
- /health result: `200 OK` — `{"status":"ok","timestamp":"2026-08-07T11:42:12.924710+00:00"}`
- Frontend check: Opened `http://localhost:5500/index.html` — Kanban board renders correctly with To Do / In Progress / Done columns, "New Task" button visible, empty-state message "No tasks found. The board is ready." (expected, since storage is in-memory and resets on restart).
- Test command: `pytest`
- Test result: 27 passed, 27 warnings (all warnings are the same benign `httpx` deprecation notice about the `app` shortcut — not test failures) in 0.26s.

## CI evidence
- Workflow file: `.github/workflows/ci.yml`
- Latest run link: https://github.com/Hachem6666/task-tracker/actions/runs/31175646981 (run #25, "Final Project Part A: README Final Project section + verified baseline," commit `2bc6a9b`, branch `final-project`) — both jobs (`test`, `docker-verify`) passed.
- Test command used by CI: `pytest -v`
- Shortcut check: no `continue-on-error`, no `|| true`, pytest is not skipped, Python version is pinned explicitly (3.11), dependency install step is present. No shortcuts found.
- Note: 2 non-blocking annotations on this run — GitHub's own Node.js 20 deprecation warnings on `actions/checkout@v4` and `actions/setup-python@v5`. These are runner-level notices unrelated to the app and do not affect pass/fail status.

## Docker evidence
- Build command (as run in CI, since local Docker is unavailable on this corporate machine without admin rights): `docker build -t task-tracker:ci .`
- Run command (as run in CI): `docker run -d --name tt-ci -p 8000:8000 task-tracker:ci`
- /health check: passed — CI's polling loop confirmed `curl -sf http://localhost:8000/health` returned 200 before the 10-attempt timeout.
- Non-root check: confirmed — `docker exec tt-ci whoami` returned `app`, matching the expected non-root runtime user.
- No-baked-secrets check: confirmed by inspecting the Dockerfile and build log — only `app/` and installed Python packages are copied into the final image (`COPY app ./app`); no `.env` file or secrets are copied. `.dockerignore` is present and excludes local environment files.

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| `GET /health` returns 200 with `{"status": "ok", ...}` (README §4) | Ran the backend locally and opened `/health` directly in browser | Confirmed — matches README's documented response shape (timestamp value differs each run, as expected) | None needed |
| CI runs `pytest -v` on push and passes (README §7) | Checked GitHub Actions run #25 for the `final-project` branch | Confirmed — `test` job passed in 17s | None needed |
| Docker container runs as non-root user `app` (README §6) | Checked CI's `docker-verify` job log, "Verify container user is 'app'" step | Confirmed — `docker exec ... whoami` returned `app` | None needed |
