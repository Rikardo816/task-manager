from uuid import UUID

from src.application.dtos.task_list_dtos import TaskListOutput
from src.application.mappers.task_list_mapper import task_list_to_output
from src.domain.exceptions.domain_exceptions import ForbiddenError, NotFoundError
from src.domain.repositories.task_list_repository import TaskListRepository


class GetTaskListUseCase:
    def __init__(self, repo: TaskListRepository) -> None:
        self._repo = repo

    async def execute(self, task_list_id: UUID, requester_id: UUID) -> TaskListOutput:
        task_list = await self._repo.get_by_id(task_list_id)
        if not task_list:
            raise NotFoundError("TaskList", str(task_list_id))
        if task_list.owner_id != requester_id:
            raise ForbiddenError()
        return task_list_to_output(task_list)
