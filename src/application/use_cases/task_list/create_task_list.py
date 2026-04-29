from src.application.dtos.task_list_dtos import CreateTaskListInput, TaskListOutput
from src.application.mappers.task_list_mapper import task_list_to_output
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
        return task_list_to_output(await self._repo.create(task_list))
