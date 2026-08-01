from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional
from app.models import TaskCreate, TaskUpdate, TaskResponse, TaskStatus

_tasks: dict[str, TaskResponse] = {}


def _as_aware_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and store a new task from validated input.

    Args:
        payload: Validated task-creation data.

    Returns:
        TaskResponse: The stored task, with a generated id and
        created_at/updated_at both set to the current UTC time.
    """
    task_id = str(uuid4())
    now = datetime.now(timezone.utc)
    task = TaskResponse(
        id=task_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        due_date=payload.due_date,
        tags=payload.tags,
        created_at=now,
        updated_at=now,
    )
    _tasks[task_id] = task
    return task


def get_all_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    overdue: Optional[bool] = None,
    tag: Optional[str] = None,
) -> list[TaskResponse]:
    """Return stored tasks, optionally filtered.

    Args:
        status: If provided, only tasks whose status value equals this string
            are returned.
        priority: If provided, only tasks whose priority value equals this
            string are returned.
        overdue: If True, only tasks with a due_date in the past (compared
            against the current UTC time, with naive due_date values treated
            as UTC via _as_aware_utc) and status != Done are returned. Any
            other value (False or None) leaves this filter unapplied.
        tag: If provided, only tasks with a tag matching this value
            case-insensitively are returned.

    Returns:
        list[TaskResponse]: Tasks matching all provided filters, in dict
        insertion order.
    """
    tasks = list(_tasks.values())
    if status:
        tasks = [t for t in tasks if t.status.value == status]
    if priority:
        tasks = [t for t in tasks if t.priority.value == priority]
    if overdue is True:
        now = datetime.now(timezone.utc)
        tasks = [
            t for t in tasks
            if t.due_date is not None
            and _as_aware_utc(t.due_date) < now
            and t.status != TaskStatus.DONE
        ]
    if tag:
        tag_lower = tag.lower()
        tasks = [t for t in tasks if any(tag_lower == existing.lower() for existing in t.tags)]
    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Look up a task by id.

    Args:
        task_id: The id to look up.

    Returns:
        Optional[TaskResponse]: The task if found, otherwise None.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to a stored task.

    Only fields explicitly set on `payload` (per
    payload.model_dump(exclude_unset=True)) are applied; fields omitted from
    the original request are left unchanged. Values are applied directly via
    setattr and are not re-validated against TaskResponse's field
    constraints, since TaskResponse.model_config does not enable
    validate_assignment — this is safe in practice because TaskUpdate's own
    field validators (see app/models.py) already reject the values that
    would otherwise violate TaskResponse's field types, e.g. explicit null
    title/tags are rejected before payload reaches this function.

    Args:
        task_id: The id of the task to update.
        payload: Fields to update; unset fields are ignored.

    Returns:
        Optional[TaskResponse]: The updated task, or None if no task with
        task_id exists. updated_at is refreshed to the current UTC time
        whenever the task is found, even if no fields changed.
    """
    if task_id not in _tasks:
        return None

    task = _tasks[task_id]
    updates = payload.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(task, field, value)

    task.updated_at = datetime.now(timezone.utc)
    return task


def delete_task(task_id: str) -> bool:
    """Delete a task by id.

    Args:
        task_id: The id of the task to delete.

    Returns:
        bool: True if a task with this id existed and was deleted, False
        otherwise.
    """
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


def _reset() -> None:
    _tasks.clear()