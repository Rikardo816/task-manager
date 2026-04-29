from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.task_list import TaskList


class TaskListRepository(ABC):
    @abstractmethod
    async def get_by_id(self, task_list_id: UUID) -> TaskList | None: ...

    @abstractmethod
    async def get_all_by_owner(self, owner_id: UUID) -> list[TaskList]: ...

    @abstractmethod
    async def create(self, task_list: TaskList) -> TaskList: ...

    @abstractmethod
    async def update(self, task_list: TaskList) -> TaskList: ...

    @abstractmethod
    async def delete(self, task_list_id: UUID) -> None: ...
