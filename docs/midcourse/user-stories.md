# User Stories

## Feature 1: Due dates + overdue filter

1. **As a user, I want to optionally set a due date when creating a task, so I can track deadlines.**
   Acceptance: `POST /tasks` accepts an optional `due_date` field in ISO 8601 format; omitting it is valid (no due date).

2. **As a user, I want to update a task's due date later, so I can adjust deadlines as plans change.**
   Acceptance: `PATCH /tasks/{id}` accepts `due_date` like any other updatable field.

3. **As a user, I want the system to reject invalid date formats, so I don't accidentally save garbage data.**
   Acceptance: A malformed `due_date` (e.g. `"not-a-date"`) returns 422.

4. **As a user, I want to see which tasks are overdue at a glance, so I can prioritize my work.**
   Acceptance: Cards for tasks with a `due_date` in the past (and not "Done") show a visible "Overdue" indicator.

5. **As a user, I want to filter the board to show only overdue tasks, so I can focus on what's late.**
   Acceptance: `GET /tasks?overdue=true` returns only tasks whose due date has passed and aren't Done.

**AI assumption corrected:** The AI's initial framing did not specify whether a Done task with a past due date should count as overdue. I confirmed with the AI that Done tasks should never show as overdue, regardless of due date — this was made explicit before implementation and covered by a dedicated test.

## Feature 2: Tags / labels

1. **As a user, I want to add tags to a task when creating it, so I can categorize work by topic or context.**
   Acceptance: `POST /tasks` accepts an optional `tags` field (list of strings); omitting it defaults to an empty list.

2. **As a user, I want tags to be trimmed and non-empty, so I don't end up with junk tags like blank strings.**
   Acceptance: Any tag that is empty or whitespace-only after trimming is rejected with 422.

3. **As a user, I want to update a task's tags later, so I can re-categorize as priorities shift.**
   Acceptance: `PATCH /tasks/{id}` accepts a new `tags` list, replacing the old one.

4. **As a user, I want to see tags displayed on each card, so I can quickly identify what a task relates to.**
   Acceptance: Cards show tag chips for every tag on the task; tasks with no tags show no chips.

5. **As a user, I want to filter tasks by tag, so I can find related work quickly.**
   Acceptance: `GET /tasks?tag=backend` returns only tasks that include that tag (case-insensitive match).

**AI assumption corrected:** The AI proposed no cap on tag count or length by default. I decided on a limit of 10 tags per task and 30 characters per tag, to prevent abuse while keeping the implementation simple.