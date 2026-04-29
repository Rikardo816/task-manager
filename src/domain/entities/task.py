from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from src.domain.value_objects.enums import Priority, TaskStatus


@dataclass
class Task:
    title: str
    task_list_id: UUID
    id: UUID = field(default_factory=uuid4)
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM
    assignee_id: UUID | None = None
    due_date: date | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def change_status(self, new_status: TaskStatus) -> None:
        self.status = new_status
        self.updated_at = datetime.now(UTC)

    def assign_to(self, user_id: UUID) -> None:
        self.assignee_id = user_id
        self.updated_at = datetime.now(UTC)

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        priority: Priority | None = None,
        assignee_id: UUID | None = None,
        due_date: date | None = None,
    ) -> None:
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if priority is not None:
            self.priority = priority
        if assignee_id is not None:
            self.assignee_id = assignee_id
        if due_date is not None:
            self.due_date = due_date
        self.updated_at = datetime.now(UTC)
