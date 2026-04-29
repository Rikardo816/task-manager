from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.value_objects.enums import Priority, TaskStatus


class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    priority: Priority = Priority.MEDIUM
    assignee_id: UUID | None = None
    due_date: date | None = None


class TaskUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    priority: Priority | None = None
    assignee_id: UUID | None = None
    due_date: date | None = None


class ChangeStatusRequest(BaseModel):
    status: TaskStatus


class AssignTaskRequest(BaseModel):
    assignee_id: UUID


class TaskResponse(BaseModel):
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

    model_config = {"from_attributes": True}


class TaskListWithCompletionResponse(BaseModel):
    tasks: list[TaskResponse]
    completion_percentage: float
    total_tasks: int
    completed_tasks: int
