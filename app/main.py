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
    description="Module 1 skeleton for the AI-Assisted Coding Task Tracker project.",
    version="0.1.0",
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
    """Simple health check endpoint used to verify the server is running."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
) -> list[TaskResponse]:
    return storage.get_all_tasks(status=status, priority=priority)


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    return storage.add_task(payload)
@app.get("/tasks/{task_id}", tags=["tasks"], response_model=TaskResponse)
def get_task_by_id(task_id: str):
    task = storage.get_task_by_id(task_id)
    if task:
        return task
    raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task_route(task_id: str, payload: TaskUpdate) -> TaskResponse:
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
    deleted = storage.delete_task(task_id)
    if deleted:
        return None
    raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")