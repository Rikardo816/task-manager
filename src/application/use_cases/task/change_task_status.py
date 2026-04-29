from uuid import UUID

from src.application.dtos.task_dtos import TaskOutput
from src.application.mappers.task_mapper import task_to_output
from src.domain.exceptions.domain_exceptions import ForbiddenError, NotFoundError
from src.domain.repositories.task_list_repository import TaskListRepository
from src.domain.repositories.task_repository import TaskRepository
from src.domain.value_objects.enums import TaskStatus


class ChangeTaskStatusUseCase:
    def __init__(
        self, task_repo: TaskRepository, task_list_repo: TaskListRepository
    ) -> None:
        self._task_repo = task_repo
        self._task_list_repo = task_list_repo

    async def execute(
        self,
        task_id: UUID,
        task_list_id: UUID,
        new_status: TaskStatus,
        requester_id: UUID,
    ) -> TaskOutput:
        task_list = await self._task_list_repo.get_by_id(task_list_id)
        if not task_list:
            raise NotFoundError("TaskList", str(task_list_id))
        if task_list.owner_id != requester_id:
            raise ForbiddenError()

        task = await self._task_repo.get_by_id(task_id)
        if not task or task.task_list_id != task_list_id:
            raise NotFoundError("Task", str(task_id))

        task.change_status(new_status)
        return task_to_output(await self._task_repo.update(task))
