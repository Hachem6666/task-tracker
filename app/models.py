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
        """Normalize and validate a task title.

        Strips leading/trailing whitespace, then rejects a blank title or a
        title longer than 200 characters (measured after stripping).

        Args:
            v: The raw title value.

        Returns:
            str: The stripped title.

        Raises:
            ValueError: If the stripped title is empty or exceeds 200 characters.
        """
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be blank")
        if len(v) > 200:
            raise ValueError("Title must be 200 characters or less")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate and normalize a task's tags.

        Rejects more than 10 tags. Each tag is stripped of leading/trailing
        whitespace; a blank tag or a tag longer than 30 characters (both
        measured after stripping) is rejected.

        Args:
            v: The raw list of tags.

        Returns:
            list[str]: The stripped tags, in their original order.

        Raises:
            ValueError: If there are more than 10 tags, a tag is blank after
                stripping, or a tag exceeds 30 characters after stripping.
        """
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
        """Normalize and validate a task title for a partial update.

        Rejects an explicit null title (title: null in the request body). If
        a non-null title is given, strips whitespace and rejects a blank or
        overlong (>200 chars) result, same as TaskCreate.validate_title.
        Omitting `title` from the request body entirely does not invoke this
        validator (Pydantic only runs field validators on fields present in
        the input; see CLAUDE.md's PATCH null-title note).

        Args:
            v: The raw title value, or None if explicitly set to null.

        Returns:
            str: The stripped title.

        Raises:
            ValueError: If v is None, or if the stripped title is empty or
                exceeds 200 characters.
        """
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
    def validate_tags(cls, v: Optional[list[str]]) -> list[str]:
        """Validate and normalize tags for a partial update.

        Rejects an explicit null tags value (tags: null in the request
        body), same as TaskUpdate.validate_title does for title. Otherwise
        applies the same rules as TaskCreate.validate_tags: at most 10 tags,
        each stripped and rejected if blank or over 30 characters after
        stripping. Omitting `tags` from the request body entirely does not
        invoke this validator, so existing tags are left unchanged.

        Args:
            v: The raw list of tags, or None if explicitly set to null.

        Returns:
            list[str]: The stripped tags, in their original order.

        Raises:
            ValueError: If v is None, if there are more than 10 tags, if a
                tag is blank after stripping, or if a tag exceeds 30
                characters after stripping.
        """
        if v is None:
            raise ValueError("Tags cannot be null")
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