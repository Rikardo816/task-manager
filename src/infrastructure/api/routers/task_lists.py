from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.task_list_dtos import CreateTaskListInput, UpdateTaskListInput
from src.application.use_cases.task_list.create_task_list import CreateTaskListUseCase
from src.application.use_cases.task_list.delete_task_list import DeleteTaskListUseCase
from src.application.use_cases.task_list.get_task_list import GetTaskListUseCase
from src.application.use_cases.task_list.list_task_lists import ListTaskListsUseCase
from src.application.use_cases.task_list.update_task_list import UpdateTaskListUseCase
from src.infrastructure.api.dependencies import get_current_user_id, get_db
from src.infrastructure.api.schemas.task_list_schemas import (
    TaskListCreateRequest,
    TaskListResponse,
    TaskListUpdateRequest,
)
from src.infrastructure.repositories.sqlalchemy_task_list_repository import (
    SQLAlchemyTaskListRepository,
)

router = APIRouter()


def _repo(db: AsyncSession) -> SQLAlchemyTaskListRepository:
    return SQLAlchemyTaskListRepository(db)


@router.get("", response_model=list[TaskListResponse])
async def list_task_lists(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[TaskListResponse]:
    result = await ListTaskListsUseCase(_repo(db)).execute(owner_id=user_id)
    return [TaskListResponse(**vars(r)) for r in result]


@router.post("", response_model=TaskListResponse, status_code=status.HTTP_201_CREATED)
async def create_task_list(
    body: TaskListCreateRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskListResponse:
    result = await CreateTaskListUseCase(_repo(db)).execute(
        CreateTaskListInput(
            name=body.name, owner_id=user_id, description=body.description
        )
    )
    return TaskListResponse(**vars(result))


@router.get("/{task_list_id}", response_model=TaskListResponse)
async def get_task_list(
    task_list_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskListResponse:
    result = await GetTaskListUseCase(_repo(db)).execute(
        task_list_id=task_list_id, requester_id=user_id
    )
    return TaskListResponse(**vars(result))


@router.put("/{task_list_id}", response_model=TaskListResponse)
async def update_task_list(
    task_list_id: UUID,
    body: TaskListUpdateRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskListResponse:
    result = await UpdateTaskListUseCase(_repo(db)).execute(
        task_list_id=task_list_id,
        input_data=UpdateTaskListInput(name=body.name, description=body.description),
        requester_id=user_id,
    )
    return TaskListResponse(**vars(result))


@router.delete("/{task_list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_list(
    task_list_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await DeleteTaskListUseCase(_repo(db)).execute(
        task_list_id=task_list_id, requester_id=user_id
    )
