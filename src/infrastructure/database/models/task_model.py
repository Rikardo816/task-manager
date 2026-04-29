import uuid
from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.value_objects.enums import Priority, TaskStatus
from src.infrastructure.database.models.base import Base


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(TaskStatus, name="task_status_enum"),
        default=TaskStatus.TODO,
        nullable=False,
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        Enum(Priority, name="priority_enum"),
        default=Priority.MEDIUM,
        nullable=False,
        index=True,
    )
    task_list_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("task_lists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    task_list: Mapped["TaskListModel"] = relationship(  # noqa: F821
        "TaskListModel", back_populates="tasks", lazy="noload"
    )
