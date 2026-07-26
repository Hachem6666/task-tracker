from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: list[str] = []

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be blank")
        if len(v) > 200:
            raise ValueError("Title must be 200 characters or less")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        if len(v) > 10:
            raise ValueError("A task can have at most 10 tags")
        cleaned = []
        for tag in v:
            tag = tag.strip()
            if not tag:
                raise ValueError("Tags cannot be blank")
            if len(tag) > 30:
                raise ValueError("Each tag must be 30 characters or less")
            cleaned.append(tag)
        return cleaned


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[list[str]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            raise ValueError("Title cannot be null")
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be blank")
        if len(v) > 200:
            raise ValueError("Title must be 200 characters or less")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is None:
            return v
        if len(v) > 10:
            raise ValueError("A task can have at most 10 tags")
        cleaned = []
        for tag in v:
            tag = tag.strip()
            if not tag:
                raise ValueError("Tags cannot be blank")
            if len(tag) > 30:
                raise ValueError("Each tag must be 30 characters or less")
            cleaned.append(tag)
        return cleaned


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime] = None
    tags: list[str] = []