from src.application.dtos.task_list_dtos import CreateTaskListInput, TaskListOutput
from src.domain.entities.task_list import TaskList
from src.domain.repositories.task_list_repository import TaskListRepository


class CreateTaskListUseCase:
    def __init__(self, repo: TaskListRepository) -> None:
        self._repo = repo

    async def execute(self, input_data: CreateTaskListInput) -> TaskListOutput:
        task_list = TaskList(
            name=input_data.name,
            owner_id=input_data.owner_id,
            description=input_data.description,
        )
        created = await self._repo.create(task_list)
        return _to_output(created)


def _to_output(tl: TaskList) -> TaskListOutput:
    return TaskListOutput(
        id=tl.id,
        name=tl.name,
        owner_id=tl.owner_id,
        description=tl.description,
        created_at=tl.created_at,
        updated_at=tl.updated_at,
    )
