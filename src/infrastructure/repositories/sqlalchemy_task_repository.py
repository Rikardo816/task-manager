from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.task import Task
from src.domain.repositories.task_repository import TaskRepository
from src.domain.value_objects.enums import Priority, TaskStatus
from src.infrastructure.database.models.task_model import TaskModel


class SQLAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, m: TaskModel) -> Task:
        return Task(
            id=m.id,
            title=m.title,
            task_list_id=m.task_list_id,
            description=m.description,
            status=m.status,
            priority=m.priority,
            assignee_id=m.assignee_id,
            due_date=m.due_date,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    async def get_by_id(self, task_id: UUID) -> Task | None:
        row = await self._session.scalar(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        return self._to_entity(row) if row else None

    async def get_all_by_task_list(
        self,
        task_list_id: UUID,
        status: TaskStatus | None = None,
        priority: Priority | None = None,
    ) -> list[Task]:
        query = (
            select(TaskModel)
            .where(TaskModel.task_list_id == task_list_id)
            .order_by(TaskModel.created_at.desc())
        )
        if status is not None:
            query = query.where(TaskModel.status == status)
        if priority is not None:
            query = query.where(TaskModel.priority == priority)

        result = await self._session.scalars(query)
        return [self._to_entity(r) for r in result.all()]

    async def count_tasks_summary(self, task_list_id: UUID) -> tuple[int, int]:
        total = await self._session.scalar(
            select(func.count()).where(TaskModel.task_list_id == task_list_id)
        )
        completed = await self._session.scalar(
            select(func.count()).where(
                TaskModel.task_list_id == task_list_id,
                TaskModel.status == TaskStatus.DONE,
            )
        )
        return total or 0, completed or 0

    async def create(self, task: Task) -> Task:
        model = TaskModel(
            id=task.id,
            title=task.title,
            task_list_id=task.task_list_id,
            description=task.description,
            status=task.status,
            priority=task.priority,
            assignee_id=task.assignee_id,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, task: Task) -> Task:
        await self._session.execute(
            sa_update(TaskModel)
            .where(TaskModel.id == task.id)
            .values(
                title=task.title,
                description=task.description,
                status=task.status,
                priority=task.priority,
                assignee_id=task.assignee_id,
                due_date=task.due_date,
                updated_at=task.updated_at,
            )
        )
        await self._session.flush()
        return task

    async def delete(self, task_id: UUID) -> None:
        model = await self._session.scalar(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        if model:
            await self._session.delete(model)
            await self._session.flush()
