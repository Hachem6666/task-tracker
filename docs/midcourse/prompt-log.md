# Prompt Log

## Feature 1: Due dates + overdue filter

**Prompt 1 (planning):** Asked the assistant to identify what was missing in `models.py`, `storage.py`, `main.py`, and `test_tasks.py` to support the due-date/tags ADR, and to propose a plan without writing code yet.
- AI returned: An accurate gap analysis and an implementation plan, correctly noting that overdue status should be computed live, not stored as a persistent field.
- Accepted: The full plan, as-is — it matched the ADR decisions exactly.

**Prompt 2 (implementation):** Asked for exact code changes to `models.py` only (one file at a time, per course workflow rules), adding `due_date` and `tags` fields plus tag validation.
- AI returned: Correct field additions and validators, but with an indentation error (the `@field_validator("tags")` block wasn't indented into the class, and a stray leading space broke a class declaration).
- Edited: Manually fixed the indentation before running tests; verified with the full pytest suite (18 passed) before proceeding.

**Prompt 3 (debugging, weak → strong):**
- Weak version (what I initially tried): "Why are my overdue and tag filters not working?"
- Strong version (what I actually used, after adding debug prints myself): Added targeted `print()` statements in both the route and storage layer to check exactly what value `overdue` and `tag` held at each step, then re-ran the specific failing test with `-s` to see the output.
- AI returned: Guidance to isolate the failure by checking route-level vs storage-level values separately.
- Accepted: The debug-print approach; it revealed the failing tests were caused by a stale saved file / pytest cache, not a logic bug — resolved by clearing `.pytest_cache` and `__pycache__` and reconfirming the save.

## Feature 2: Tags / labels

**Prompt 1 (Break Test, E3-style):** Asked the assistant for the smallest temporary source change that would make `test_list_tasks_filter_overdue_returns_only_overdue_tasks` fail, to prove the test is meaningful.
- AI returned: Flip the comparison operator in the overdue filter from `<` to `>`.
- Accepted: Applied the change, confirmed the test failed with the exact predicted assertion mismatch, then reverted immediately.

**Prompt 2 (frontend wiring):** Asked for the exact diff to add `due_date` and `tags` fields to the modal's read/pre-fill/submit logic, matching the existing code's variable naming and structure.
- AI returned: Six precise edits (field references, pre-fill, payload building, task mapping, card rendering).
- Accepted: All six edits, applied manually one at a time; verified visually in the browser (tag chips and overdue pill rendering correctly, edit pre-fill working).

**Prompt 3 (test generation):** Asked for one pytest test per new scenario (create with due date/tags, reject blank tag, reject too many tags, overdue filter, Done exclusion, tag filter case-insensitivity).
- AI returned: Six well-scoped tests matching the existing test file's style and fixture pattern.
- Edited: Fixed a paste-indentation error where one new test was accidentally nested inside another (later diagnosed and corrected).