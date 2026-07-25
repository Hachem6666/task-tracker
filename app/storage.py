from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional
from app.models import TaskCreate, TaskUpdate, TaskResponse, TaskStatus

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
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
            and t.due_date < now
            and t.status != TaskStatus.DONE
        ]
    if tag:
        tag_lower = tag.lower()
        tasks = [t for t in tasks if any(tag_lower == existing.lower() for existing in t.tags)]
    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    if task_id not in _tasks:
        return None

    task = _tasks[task_id]
    updates = payload.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(task, field, value)

    task.updated_at = datetime.now(timezone.utc)
    return task


def delete_task(task_id: str) -> bool:
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


def _reset() -> None:
    _tasks.clear()