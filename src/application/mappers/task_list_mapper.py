from src.application.dtos.task_list_dtos import TaskListOutput
from src.domain.entities.task_list import TaskList


def task_list_to_output(task_list: TaskList) -> TaskListOutput:
    return TaskListOutput(
        id=task_list.id,
        name=task_list.name,
        owner_id=task_list.owner_id,
        description=task_list.description,
        created_at=task_list.created_at,
        updated_at=task_list.updated_at,
    )
