from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.task_list import TaskList
from src.domain.repositories.task_list_repository import TaskListRepository
from src.infrastructure.database.models.task_list_model import TaskListModel


class SQLAlchemyTaskListRepository(TaskListRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, m: TaskListModel) -> TaskList:
        return TaskList(
            id=m.id,
            name=m.name,
            owner_id=m.owner_id,
            description=m.description,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    async def get_by_id(self, task_list_id: UUID) -> TaskList | None:
        row = await self._session.scalar(
            select(TaskListModel).where(TaskListModel.id == task_list_id)
        )
        return self._to_entity(row) if row else None

    async def get_all_by_owner(self, owner_id: UUID) -> list[TaskList]:
        result = await self._session.scalars(
            select(TaskListModel)
            .where(TaskListModel.owner_id == owner_id)
            .order_by(TaskListModel.created_at.desc())
        )
        return [self._to_entity(r) for r in result.all()]

    async def create(self, task_list: TaskList) -> TaskList:
        model = TaskListModel(
            id=task_list.id,
            name=task_list.name,
            owner_id=task_list.owner_id,
            description=task_list.description,
            created_at=task_list.created_at,
            updated_at=task_list.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, task_list: TaskList) -> TaskList:
        model = await self._session.scalar(
            select(TaskListModel).where(TaskListModel.id == task_list.id)
        )
        if not model:
            raise ValueError(f"TaskList {task_list.id} not found for update")
        model.name = task_list.name
        model.description = task_list.description
        model.updated_at = task_list.updated_at
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, task_list_id: UUID) -> None:
        model = await self._session.scalar(
            select(TaskListModel).where(TaskListModel.id == task_list_id)
        )
        if model:
            await self._session.delete(model)
            await self._session.flush()
