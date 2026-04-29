from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class CreateTaskListInput:
    name: str
    owner_id: UUID
    description: str | None = None


@dataclass
class UpdateTaskListInput:
    name: str | None = None
    description: str | None = None


@dataclass
class TaskListOutput:
    id: UUID
    name: str
    owner_id: UUID
    description: str | None
    created_at: datetime
    updated_at: datetime
