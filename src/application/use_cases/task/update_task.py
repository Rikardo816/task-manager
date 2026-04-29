from datetime import UTC, datetime
from uuid import UUID

from src.application.dtos.task_dtos import TaskOutput, UpdateTaskInput
from src.application.use_cases.task.create_task import _to_output
from src.domain.exceptions.domain_exceptions import ForbiddenError, NotFoundError
from src.domain.repositories.task_list_repository import TaskListRepository
from src.domain.repositories.task_repository import TaskRepository


class UpdateTaskUseCase:
    def __init__(
        self, task_repo: TaskRepository, task_list_repo: TaskListRepository
    ) -> None:
        self._task_repo = task_repo
        self._task_list_repo = task_list_repo

    async def execute(
        self,
        task_id: UUID,
        task_list_id: UUID,
        input_data: UpdateTaskInput,
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

        if input_data.title is not None:
            task.title = input_data.title
        if input_data.description is not None:
            task.description = input_data.description
        if input_data.priority is not None:
            task.priority = input_data.priority
        if input_data.assignee_id is not None:
            task.assignee_id = input_data.assignee_id
        if input_data.due_date is not None:
            task.due_date = input_data.due_date
        task.updated_at = datetime.now(UTC)

        return _to_output(await self._task_repo.update(task))
