from datetime import datetime
from uuid import UUID

from src.application.dtos.task_list_dtos import TaskListOutput, UpdateTaskListInput
from src.application.use_cases.task_list.create_task_list import _to_output
from src.domain.exceptions.domain_exceptions import ForbiddenError, NotFoundError
from src.domain.repositories.task_list_repository import TaskListRepository


class UpdateTaskListUseCase:
    def __init__(self, repo: TaskListRepository) -> None:
        self._repo = repo

    async def execute(
        self,
        task_list_id: UUID,
        input_data: UpdateTaskListInput,
        requester_id: UUID,
    ) -> TaskListOutput:
        task_list = await self._repo.get_by_id(task_list_id)
        if not task_list:
            raise NotFoundError("TaskList", str(task_list_id))
        if task_list.owner_id != requester_id:
            raise ForbiddenError()

        if input_data.name is not None:
            task_list.name = input_data.name
        if input_data.description is not None:
            task_list.description = input_data.description
        task_list.updated_at = datetime.utcnow()

        return _to_output(await self._repo.update(task_list))
