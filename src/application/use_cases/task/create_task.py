from uuid import UUID

from src.application.dtos.task_dtos import CreateTaskInput, TaskOutput
from src.application.mappers.task_mapper import task_to_output
from src.domain.entities.task import Task
from src.domain.exceptions.domain_exceptions import ForbiddenError, NotFoundError
from src.domain.repositories.task_list_repository import TaskListRepository
from src.domain.repositories.task_repository import TaskRepository


class CreateTaskUseCase:
    def __init__(
        self, task_repo: TaskRepository, task_list_repo: TaskListRepository
    ) -> None:
        self._task_repo = task_repo
        self._task_list_repo = task_list_repo

    async def execute(
        self, input_data: CreateTaskInput, requester_id: UUID
    ) -> TaskOutput:
        task_list = await self._task_list_repo.get_by_id(input_data.task_list_id)
        if not task_list:
            raise NotFoundError("TaskList", str(input_data.task_list_id))
        if task_list.owner_id != requester_id:
            raise ForbiddenError()

        task = Task(
            title=input_data.title,
            task_list_id=input_data.task_list_id,
            description=input_data.description,
            priority=input_data.priority,
            assignee_id=input_data.assignee_id,
            due_date=input_data.due_date,
        )
        return task_to_output(await self._task_repo.create(task))
