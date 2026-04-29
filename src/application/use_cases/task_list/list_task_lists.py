from uuid import UUID

from src.application.dtos.task_list_dtos import TaskListOutput
from src.application.use_cases.task_list.create_task_list import _to_output
from src.domain.repositories.task_list_repository import TaskListRepository


class ListTaskListsUseCase:
    def __init__(self, repo: TaskListRepository) -> None:
        self._repo = repo

    async def execute(self, owner_id: UUID) -> list[TaskListOutput]:
        return [_to_output(tl) for tl in await self._repo.get_all_by_owner(owner_id)]
