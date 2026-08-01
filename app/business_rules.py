from fastapi import HTTPException, status
from app.models import TaskStatus

VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset({
    (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
    (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
    (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
})


def validate_status_transition(current: TaskStatus, new: TaskStatus) -> None:
    """Validate that a task status transition is allowed.

    Checks (current, new) against VALID_TRANSITIONS. A same-status transition
    (e.g. ToDo -> ToDo) is not in VALID_TRANSITIONS and is therefore rejected.

    Args:
        current: The task's current status.
        new: The requested new status.

    Returns:
        None: Returns nothing if the transition is valid.

    Raises:
        HTTPException: 422 Unprocessable Entity if (current, new) is not in
            VALID_TRANSITIONS. The error detail lists all allowed transitions.
    """
    # Same -> same is invalid. Anything not in VALID_TRANSITIONS is invalid.
    if (current, new) not in VALID_TRANSITIONS:
        allowed = sorted({f"{f.value}->{t.value}" for f, t in VALID_TRANSITIONS})
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status transition from {current.value} to {new.value}. Allowed transitions: {allowed}",
        )
