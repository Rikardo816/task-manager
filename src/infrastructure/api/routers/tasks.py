from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

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
from src.domain.value_objects.enums import Priority, TaskStatus
from src.infrastructure.api.dependencies import get_current_user_id, get_db
from src.infrastructure.api.schemas.task_schemas import (
    AssignTaskRequest,
    ChangeStatusRequest,
    TaskCreateRequest,
    TaskListWithCompletionResponse,
    TaskResponse,
    TaskUpdateRequest,
)
from src.infrastructure.repositories.sqlalchemy_task_list_repository import (
    SQLAlchemyTaskListRepository,
)
from src.infrastructure.repositories.sqlalchemy_task_repository import (
    SQLAlchemyTaskRepository,
)
from src.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

router = APIRouter()

_BASE = "/{task_list_id}/tasks"


def _task_repo(db: AsyncSession) -> SQLAlchemyTaskRepository:
    return SQLAlchemyTaskRepository(db)


def _task_list_repo(db: AsyncSession) -> SQLAlchemyTaskListRepository:
    return SQLAlchemyTaskListRepository(db)


@router.get(_BASE, response_model=TaskListWithCompletionResponse)
async def list_tasks(
    task_list_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: TaskStatus | None = Query(None, alias="status"),
    priority_filter: Priority | None = Query(None, alias="priority"),
) -> TaskListWithCompletionResponse:
    result = await ListTasksUseCase(_task_repo(db), _task_list_repo(db)).execute(
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
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
    result = await CreateTaskUseCase(_task_repo(db), _task_list_repo(db)).execute(
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
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
    result = await GetTaskUseCase(_task_repo(db), _task_list_repo(db)).execute(
        task_id=task_id, task_list_id=task_list_id, requester_id=user_id
    )
    return TaskResponse(**vars(result))


@router.put(_BASE + "/{task_id}", response_model=TaskResponse)
async def update_task(
    task_list_id: UUID,
    task_id: UUID,
    body: TaskUpdateRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
    result = await UpdateTaskUseCase(_task_repo(db), _task_list_repo(db)).execute(
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
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await DeleteTaskUseCase(_task_repo(db), _task_list_repo(db)).execute(
        task_id=task_id, task_list_id=task_list_id, requester_id=user_id
    )


@router.patch(_BASE + "/{task_id}/status", response_model=TaskResponse)
async def change_task_status(
    task_list_id: UUID,
    task_id: UUID,
    body: ChangeStatusRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
    result = await ChangeTaskStatusUseCase(_task_repo(db), _task_list_repo(db)).execute(
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
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
    result = await AssignTaskUseCase(
        _task_repo(db),
        _task_list_repo(db),
        SQLAlchemyUserRepository(db),
        NotificationService(),
    ).execute(
        task_id=task_id,
        task_list_id=task_list_id,
        assignee_id=body.assignee_id,
        requester_id=user_id,
    )
    return TaskResponse(**vars(result))
