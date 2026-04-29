from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.task import Task
from src.domain.value_objects.enums import Priority, TaskStatus


class TaskRepository(ABC):
    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> Task | None: ...

    @abstractmethod
    async def get_all_by_task_list(
        self,
        task_list_id: UUID,
        status: TaskStatus | None = None,
        priority: Priority | None = None,
    ) -> list[Task]: ...

    @abstractmethod
    async def count_by_task_list(self, task_list_id: UUID) -> int: ...

    @abstractmethod
    async def count_completed_by_task_list(self, task_list_id: UUID) -> int: ...

    @abstractmethod
    async def create(self, task: Task) -> Task: ...

    @abstractmethod
    async def update(self, task: Task) -> Task: ...

    @abstractmethod
    async def delete(self, task_id: UUID) -> None: ...
