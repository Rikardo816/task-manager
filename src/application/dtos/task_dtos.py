from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID

from src.domain.value_objects.enums import Priority, TaskStatus


@dataclass
class CreateTaskInput:
    title: str
    task_list_id: UUID
    description: str | None = None
    priority: Priority = Priority.MEDIUM
    assignee_id: UUID | None = None
    due_date: date | None = None


@dataclass
class UpdateTaskInput:
    title: str | None = None
    description: str | None = None
    priority: Priority | None = None
    assignee_id: UUID | None = None
    due_date: date | None = None


@dataclass
class ListTasksInput:
    task_list_id: UUID
    status: TaskStatus | None = None
    priority: Priority | None = None


@dataclass
class TaskOutput:
    id: UUID
    title: str
    task_list_id: UUID
    status: TaskStatus
    priority: Priority
    description: str | None
    assignee_id: UUID | None
    due_date: date | None
    created_at: datetime
    updated_at: datetime


@dataclass
class TaskListWithCompletionOutput:
    tasks: list[TaskOutput]
    completion_percentage: float
    total_tasks: int
    completed_tasks: int = field(default=0)
