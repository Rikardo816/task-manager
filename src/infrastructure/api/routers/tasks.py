from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.application.dtos.task_dtos import (
    CreateTaskInput,
    ListTasksInput,
    UpdateTaskInput,
)
from src.application.services.notification_service import NotificationService
from src.application.use_cases.task.assign_task import AssignTaskUseCase
from src.application.use_cases.task.change_task_status import ChangeTaskStatusUseCase
from src.application.use_cases.task.create_task import CreateTaskUseCase
from src.application.use_cases.task.delete_task import DeleteTaskUseCase
from src.application.use_cases.task.get_task import GetTaskUseCase
from src.application.use_cases.task.list_tasks import ListTasksUseCase
from src.application.use_cases.task.update_task import UpdateTaskUseCase
from src.domain.repositories.task_list_repository import TaskListRepository
from src.domain.repositories.task_repository import TaskRepository
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.enums import Priority, TaskStatus
from src.infrastructure.api.dependencies import (
    CurrentUser,
    get_current_user,
    get_current_user_id,
    get_task_list_repo,
    get_task_repo,
    get_user_repo,
)
from src.infrastructure.api.schemas.task_schemas import (
    AssignTaskRequest,
    ChangeStatusRequest,
    TaskCreateRequest,
    TaskListWithCompletionResponse,
    TaskResponse,
    TaskUpdateRequest,
)

router = APIRouter()

_BASE = "/{task_list_id}/tasks"

_notification_service = NotificationService()


@router.get(_BASE, response_model=TaskListWithCompletionResponse)
async def list_tasks(
    task_list_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    task_repo: Annotated[TaskRepository, Depends(get_task_repo)],
    task_list_repo: Annotated[TaskListRepository, Depends(get_task_list_repo)],
    status_filter: TaskStatus | None = Query(None, alias="status"),
    priority_filter: Priority | None = Query(None, alias="priority"),
) -> TaskListWithCompletionResponse:
    result = await ListTasksUseCase(task_repo, task_list_repo).execute(
        ListTasksInput(
            task_list_id=task_list_id,
            status=status_filter,
            priority=priority_filter,
        ),
        requester_id=user_id,
    )
    return TaskListWithCompletionResponse(
        tasks=[TaskResponse(**vars(t)) for t in result.tasks],
        completion_percentage=result.completion_percentage,
        total_tasks=result.total_tasks,
        completed_tasks=result.completed_tasks,
    )


@router.post(
    _BASE,
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task_list_id: UUID,
    body: TaskCreateRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    task_repo: Annotated[TaskRepository, Depends(get_task_repo)],
    task_list_repo: Annotated[TaskListRepository, Depends(get_task_list_repo)],
) -> TaskResponse:
    result = await CreateTaskUseCase(task_repo, task_list_repo).execute(
        CreateTaskInput(
            title=body.title,
            task_list_id=task_list_id,
            description=body.description,
            priority=body.priority,
            assignee_id=body.assignee_id,
            due_date=body.due_date,
        ),
        requester_id=user_id,
    )
    return TaskResponse(**vars(result))


@router.get(_BASE + "/{task_id}", response_model=TaskResponse)
async def get_task(
    task_list_id: UUID,
    task_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    task_repo: Annotated[TaskRepository, Depends(get_task_repo)],
    task_list_repo: Annotated[TaskListRepository, Depends(get_task_list_repo)],
) -> TaskResponse:
    result = await GetTaskUseCase(task_repo, task_list_repo).execute(
        task_id=task_id, task_list_id=task_list_id, requester_id=user_id
    )
    return TaskResponse(**vars(result))


@router.put(_BASE + "/{task_id}", response_model=TaskResponse)
async def update_task(
    task_list_id: UUID,
    task_id: UUID,
    body: TaskUpdateRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    task_repo: Annotated[TaskRepository, Depends(get_task_repo)],
    task_list_repo: Annotated[TaskListRepository, Depends(get_task_list_repo)],
) -> TaskResponse:
    result = await UpdateTaskUseCase(task_repo, task_list_repo).execute(
        task_id=task_id,
        task_list_id=task_list_id,
        input_data=UpdateTaskInput(
            title=body.title,
            description=body.description,
            priority=body.priority,
            assignee_id=body.assignee_id,
            due_date=body.due_date,
        ),
        requester_id=user_id,
    )
    return TaskResponse(**vars(result))


@router.delete(_BASE + "/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_list_id: UUID,
    task_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    task_repo: Annotated[TaskRepository, Depends(get_task_repo)],
    task_list_repo: Annotated[TaskListRepository, Depends(get_task_list_repo)],
) -> None:
    await DeleteTaskUseCase(task_repo, task_list_repo).execute(
        task_id=task_id, task_list_id=task_list_id, requester_id=user_id
    )


@router.patch(_BASE + "/{task_id}/status", response_model=TaskResponse)
async def change_task_status(
    task_list_id: UUID,
    task_id: UUID,
    body: ChangeStatusRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    task_repo: Annotated[TaskRepository, Depends(get_task_repo)],
    task_list_repo: Annotated[TaskListRepository, Depends(get_task_list_repo)],
) -> TaskResponse:
    result = await ChangeTaskStatusUseCase(task_repo, task_list_repo).execute(
        task_id=task_id,
        task_list_id=task_list_id,
        new_status=body.status,
        requester_id=user_id,
    )
    return TaskResponse(**vars(result))


@router.patch(_BASE + "/{task_id}/assignee", response_model=TaskResponse)
async def assign_task(
    task_list_id: UUID,
    task_id: UUID,
    body: AssignTaskRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    task_repo: Annotated[TaskRepository, Depends(get_task_repo)],
    task_list_repo: Annotated[TaskListRepository, Depends(get_task_list_repo)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> TaskResponse:
    result = await AssignTaskUseCase(
        task_repo,
        task_list_repo,
        user_repo,
        _notification_service,
    ).execute(
        task_id=task_id,
        task_list_id=task_list_id,
        assignee_id=body.assignee_id,
        requester_id=current_user.id,
        requester_username=current_user.username,
    )
    return TaskResponse(**vars(result))
