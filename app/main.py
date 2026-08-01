# app/main.py
# Entry point for the Task Tracker API. Creates the FastAPI app instance
# and defines a single /health endpoint used to verify the server is running.

import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, status , HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import storage
from app.business_rules import validate_status_transition
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus , TaskUpdate

# Load variables from .env (PORT, APP_ENV) into the environment.
load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")

app = FastAPI(
    title="Task Tracker API",
    description="FastAPI backend for the Task Tracker: task CRUD, status transitions, due dates/overdue filtering, and tags. Includes a GitHub Actions CI workflow and a local-only Dockerfile (Module 4).",
    version="0.4.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Pydantic model defines the exact response shape for /health,
# instead of returning a raw dict.
class HealthResponse(BaseModel):
    status: str
    timestamp: str


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Health check endpoint used to verify the server is running.

    Returns:
        HealthResponse: status "ok" and the current UTC timestamp in ISO 8601 format.
    """
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    overdue: bool | None = None,
    tag: str | None = None,
) -> list[TaskResponse]:
    """List tasks, optionally filtered by status, priority, overdue state, and tag.

    Example:
        GET /tasks?status=ToDo&priority=High&overdue=true&tag=urgent

    Args:
        status: If provided, only tasks whose status equals this value are returned.
        priority: If provided, only tasks whose priority equals this value are returned.
        overdue: If True, only tasks with a due_date in the past (relative to the
            current UTC time) and status != Done are returned. If False or omitted,
            this filter is not applied — overdue=False behaves the same as omitting
            the parameter, it does not filter out overdue tasks.
        tag: If provided, only tasks with a matching tag (case-insensitive) are
            returned.

    Returns:
        list[TaskResponse]: Tasks matching all provided filters.

    Raises:
        (via FastAPI/Pydantic) 422 Unprocessable Entity if status or priority is
        not a valid TaskStatus/TaskPriority value.
    """
    return storage.get_all_tasks(status=status, priority=priority, overdue=overdue, tag=tag)

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task.

    Example:
        POST /tasks
        {"title": "Write docs"}

    Args:
        payload: Task fields to create. Fields not provided use TaskCreate's
            defaults (status=ToDo, priority=Medium, tags=[], description="", etc.).

    Returns:
        TaskResponse: The newly created task, including a generated id and
        created_at/updated_at both set to the current UTC time.

    Raises:
        (via FastAPI/Pydantic) 422 Unprocessable Entity if payload fails
        TaskCreate validation (e.g. blank/overlong title, more than 10 tags,
        blank/overlong tag).
    """
    return storage.add_task(payload)
@app.get("/tasks/{task_id}", tags=["tasks"], response_model=TaskResponse)
def get_task_by_id(task_id: str):
    """Retrieve a single task by id.

    Example:
        GET /tasks/{task_id}

    Args:
        task_id: The id of the task to retrieve.

    Returns:
        TaskResponse: The matching task.

    Raises:
        HTTPException: 404 if no task with the given id exists.
    """
    task = storage.get_task_by_id(task_id)
    if task:
        return task
    raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task_route(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Partially update a task.

    Only fields explicitly present in the request body are changed; fields
    omitted from the body are left unchanged (see TaskUpdate and
    storage.update_task, which uses model_dump(exclude_unset=True)). If
    `status` is included in the payload, the transition from the task's
    current status to the requested status is validated against
    business_rules.VALID_TRANSITIONS before the update is applied.

    Example:
        PATCH /tasks/{task_id}
        {"status": "InProgress"}

    Args:
        task_id: The id of the task to update.
        payload: Fields to update; only fields explicitly set are applied.

    Returns:
        TaskResponse: The updated task.

    Raises:
        HTTPException: 404 if no task with the given id exists.
        HTTPException: 422 if `status` is provided and the transition from the
            task's current status to the requested status is not in
            VALID_TRANSITIONS.
        (via FastAPI/Pydantic) 422 if payload fails TaskUpdate validation
        (e.g. explicit null title, explicit null tags, more than 10 tags).
    """
    if payload.status is not None:
        existing_task = storage.get_task_by_id(task_id)
        if existing_task is None:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        validate_status_transition(existing_task.status, payload.status)

    updated_task = storage.update_task(task_id, payload)
    if updated_task:
        return updated_task
    raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task_route(task_id: str) -> None:
    """Delete a task by id.

    Example:
        DELETE /tasks/{task_id}

    Args:
        task_id: The id of the task to delete.

    Returns:
        None: No content is returned on success (204 No Content).

    Raises:
        HTTPException: 404 if no task with the given id exists.
    """
    deleted = storage.delete_task(task_id)
    if deleted:
        return None
    raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")