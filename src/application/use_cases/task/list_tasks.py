from uuid import UUID

from src.application.dtos.task_dtos import ListTasksInput, TaskListWithCompletionOutput
from src.application.use_cases.task.create_task import _to_output
from src.domain.exceptions.domain_exceptions import ForbiddenError, NotFoundError
from src.domain.repositories.task_list_repository import TaskListRepository
from src.domain.repositories.task_repository import TaskRepository


class ListTasksUseCase:
    def __init__(
        self, task_repo: TaskRepository, task_list_repo: TaskListRepository
    ) -> None:
        self._task_repo = task_repo
        self._task_list_repo = task_list_repo

    async def execute(
        self, input_data: ListTasksInput, requester_id: UUID
    ) -> TaskListWithCompletionOutput:
        task_list = await self._task_list_repo.get_by_id(input_data.task_list_id)
        if not task_list:
            raise NotFoundError("TaskList", str(input_data.task_list_id))
        if task_list.owner_id != requester_id:
            raise ForbiddenError()

        total = await self._task_repo.count_by_task_list(input_data.task_list_id)
        completed = await self._task_repo.count_completed_by_task_list(
            input_data.task_list_id
        )
        pct = round((completed / total * 100), 2) if total > 0 else 0.0

        tasks = await self._task_repo.get_all_by_task_list(
            task_list_id=input_data.task_list_id,
            status=input_data.status,
            priority=input_data.priority,
        )
        return TaskListWithCompletionOutput(
            tasks=[_to_output(t) for t in tasks],
            completion_percentage=pct,
            total_tasks=total,
            completed_tasks=completed,
        )
