# Module 5 Governance Retrospective — What I Shared With AI Coding Tools

Risk rubric:
- **Low**: public code, course toy project code, no sensitive data, no proprietary logic.
- **Medium**: private but non-sensitive code, internal implementation details, or non-public repo context with no secrets and no PII.
- **High**: credentials, tokens, secrets, production config, real customer/user data, regulated data, or code I am not authorized to share.

Repo visibility confirmed: `github.com/Hachem6666/task-tracker` is a **public** repository (confirmed from course setup).

| Item shared | Risk | Reason | Safer future version | Ambiguity to resolve |
|---|---|---|---|---|
| Source code (main.py, models.py, tests, frontend) | Low | Public, course toy project code; the inspected files (`app/main.py`, `app/models.py`, `app/business_rules.py`, `app/storage.py`) contain plain CRUD/validation logic — no secrets, tokens, or proprietary business logic. | No change needed — continue sharing plain source, never a `.env` or config with real values. | None — repo confirmed public. |
| Terminal output, pytest results, error messages | Low | Debug output from a public toy app that handles no credentials by design. | If stack traces ever include absolute local paths (`C:\Users\<name>\...`), trim or genericize them before pasting. | Haven't reviewed the literal pasted terminal transcripts from past sessions, only the app's source — can't confirm none included a full local path with a username. |
| Docs (CLAUDE.md, user stories, ADR, prompt log, verification notes) | Low | Course-authored planning docs for a public toy project; no secrets or PII evident from the file set. | Keep as-is; if any employer-specific terminology ever crept into a prompt log entry, redact before sharing docs outward. | Haven't re-read the full prompt log text to confirm no incidental employer references. |
| Small JSON task snippets used for testing | Low | Verified directly — sample payloads in `tests/test_tasks.py` are synthetic strings (e.g. "Buy milk", "Task"), not real data. | No change needed. | None — confirmed by direct inspection. |
| Screenshots (VS Code, test failures, app behaviour) | Medium | Observed, not hypothetical: some screenshots showed more than the app window — full taskbar with pinned apps, clock, and notification icons were visible in the background, alongside internal file paths, Windows username, and corporate endpoint-security (Kaspersky) branding. | Crop screenshots to just the relevant editor/terminal pane before sharing; close or hide the taskbar and notification area; consider a sanitized username or VM for course screenshots. | None outstanding for this row. |
| Course requirements/assignment instructions | Low | Instructor-provided assignment text, not employer-proprietary; shared with an AI tool for coursework on a public repo. | If course policy on redistributing assignment text to third-party tools is unclear, paraphrase rather than paste verbatim. | Whether the course's own terms restrict pasting assignment text into external AI tools — an academic-policy question outside this repo's visibility. |

**Not minimized**: Screenshots (Row 5) remain Medium based on an observed fact (taskbar/notifications visible), not a hypothetical — this is the one item here that plausibly exposed more than the code itself did. No other row was downgraded on account of project size; the Low ratings hold because specific content was verified (test data, source files, public repo status), not assumed.
