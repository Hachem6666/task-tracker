# Technical Decision Note: CI Workflow Design

**Module:** 4 (CI + local Docker verification)
**Related files:** `.github/workflows/ci.yml`

## 1. Context

The Task Tracker had no automated verification before Module 4 — tests only ran when someone remembered to run `pytest -v` locally. The project also gained a `Dockerfile` in this module (local build/run only, per `CLAUDE.md`'s Do-Not Rules, which explicitly forbid deployment steps, hosting, or orchestration). We needed a way to catch regressions on every push/PR without introducing any deployment surface, since this remains a course project with no auth, no database, and no production environment.

GitHub Actions was the natural choice since the repo already lives on GitHub and needs no separate CI account or infrastructure.

## 2. Decision

Add a single workflow file, `.github/workflows/ci.yml`, triggered on `push` and `pull_request`, with two independent jobs: `test` (installs `requirements.txt` on Python 3.11 and runs `pytest -v`) and `docker-verify` (builds the image, runs it, polls `/health`, asserts non-root user, tears down). Neither job pushes an image to a registry, logs into any external service, or deploys anywhere.

## 3. Alternatives Considered

- **Single combined job (test + docker-verify in one job):** Rejected — a Docker build failure would obscure whether the actual test suite passed.
- **No `docker-verify` job, Dockerfile unverified by CI:** Rejected — a Dockerfile that only gets exercised manually risks silently rotting.
- **Other CI providers (CircleCI, Jenkins, etc.):** Rejected without serious evaluation — GitHub Actions requires no new account or billing relationship.
- **Registry push / GHCR publish step:** Rejected — explicitly out of scope per `CLAUDE.md`'s Do-Not Rules.

## 4. Trade-offs

- Keeping the tests and Docker verification as separate jobs makes it much easier to see what actually failed. During this module I saw that a failing pytest run and Docker-related issues were different problems, so separating them makes troubleshooting simpler. The downside is that the workflow takes a little longer because both jobs run independently.
- Since I don't have Docker installed locally, I had to rely on GitHub Actions to verify that the Docker image builds and runs correctly. That gives me confidence in the Dockerfile, but it also means I can't test or debug Docker issues myself before pushing changes.
- I also had to update CLAUDE.md twice because the CI workflow and the Docker verification initially conflicted with the project rules. It showed me that keeping documentation and implementation in sync takes extra effort, but it avoids confusion later.
- I would do this differently by installing Docker locally so I can test and fix Docker-related problems before pushing to GitHub, instead of relying entirely on CI.

## 5. Consequences

- Every push and PR now gets an automatic, objective pass/fail signal for both the test suite and the containerized app's basic health and non-root posture.
- The Dockerfile is no longer purely aspirational; CI is proof it actually builds and runs on a clean machine.
- `requirements.txt` had to gain `pytest==8.4.2` as an explicit pinned dependency — a direct consequence of the `test` job needing a reproducible install.
- CI does not verify anything about deployment, hosting, authentication, or persistence, because none of those exist in this project.

## 6. Open Questions

- I'm not sure if the current health-check timeout is enough in all situations, or if it should wait a little longer before failing.
- I'm also unsure whether adding caching for dependencies or Docker layers would be worth it for such a small project, or if keeping the workflow simple is the better choice.
- If this project grows in the future, I'm not sure whether deployment should be added to this workflow or kept in a completely separate workflow to avoid mixing responsibilities.
