# Verification

## Baseline check (before any changes)
Branch `mid-course-project` created from `master`. Ran the full existing pytest suite before touching any code:
- 18 tests, all passing (0 new features yet).

## Backend test results (after both features implemented)
Ran the full pytest suite after implementing due dates, tags, overdue filter, and tag filter:
- 24 tests, all passing (18 original + 6 new).
- New tests cover: creating tasks with due date/tags, rejecting blank tags, rejecting too many tags, filtering by overdue, excluding Done tasks from overdue results, and case-insensitive tag filtering.

## Manual browser checks
- Created a task with a due date in the past and a tag ("hi" / "bye") — confirmed the card displayed a red "Overdue" badge and the tag chip.
- Created a task with a due date in the future — confirmed no "Overdue" badge appeared.
- Edited an existing task — confirmed the Due date and Tags fields pre-filled correctly with the task's existing values.
- Re-ran the full Module 3 behavior contract after adding both features:
  - Drag-and-drop between columns still works and persists via PATCH.
  - Cancel, ×, Escape, and overlay-click all still dismiss the modal correctly.
  - Empty-title validation still blocks task creation.
  - All three UI states (loading, empty, error with Retry) confirmed unaffected by the new fields.

## Break Test evidence

**Break Test 1 (Module 3, from E1-E3 exercise):**
Test: `test_patch_empty_json_object_returns_existing_task_unchanged`
Temporary break: Added a guard in `update_task_route` in `main.py` to reject empty PATCH payloads with a 422.
Result: Test failed as predicted (`assert 422 == 200`), confirming the test correctly protects the no-op PATCH behavior. Reverted immediately; full suite passed again.

**Break Test 2 (mid-course project, Feature 1):**
Test: `test_list_tasks_filter_overdue_returns_only_overdue_tasks`
Temporary break: Flipped the comparison operator in the overdue filter in `storage.py` from `due_date < now` to `due_date > now`.
Result: Test failed as predicted (`assert 'Future task' == 'Overdue task'`), confirming the test correctly detects a broken overdue filter. Reverted immediately; full suite (24 tests) passed again.