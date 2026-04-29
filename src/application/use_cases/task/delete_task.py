from uuid import UUID

from src.domain.exceptions.domain_exceptions import ForbiddenError, NotFoundError
from src.domain.repositories.task_list_repository import TaskListRepository
from src.domain.repositories.task_repository import TaskRepository


class DeleteTaskUseCase:
    def __init__(
        self, task_repo: TaskRepository, task_list_repo: TaskListRepository
    ) -> None:
        self._task_repo = task_repo
        self._task_list_repo = task_list_repo

    async def execute(
        self, task_id: UUID, task_list_id: UUID, requester_id: UUID
    ) -> None:
        task_list = await self._task_list_repo.get_by_id(task_list_id)
        if not task_list:
            raise NotFoundError("TaskList", str(task_list_id))
        if task_list.owner_id != requester_id:
            raise ForbiddenError()

        task = await self._task_repo.get_by_id(task_id)
        if not task or task.task_list_id != task_list_id:
            raise NotFoundError("Task", str(task_id))
        await self._task_repo.delete(task_id)
