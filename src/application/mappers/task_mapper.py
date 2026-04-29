from src.application.dtos.task_dtos import TaskOutput
from src.domain.entities.task import Task


def task_to_output(task: Task) -> TaskOutput:
    return TaskOutput(
        id=task.id,
        title=task.title,
        task_list_id=task.task_list_id,
        status=task.status,
        priority=task.priority,
        description=task.description,
        assignee_id=task.assignee_id,
        due_date=task.due_date,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )
