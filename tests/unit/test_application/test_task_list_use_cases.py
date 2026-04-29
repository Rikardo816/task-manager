import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from src.application.dtos.task_list_dtos import CreateTaskListInput, UpdateTaskListInput
from src.application.use_cases.task_list.create_task_list import CreateTaskListUseCase
from src.application.use_cases.task_list.delete_task_list import DeleteTaskListUseCase
from src.application.use_cases.task_list.get_task_list import GetTaskListUseCase
from src.application.use_cases.task_list.list_task_lists import ListTaskListsUseCase
from src.application.use_cases.task_list.update_task_list import UpdateTaskListUseCase
from src.domain.entities.task_list import TaskList
from src.domain.exceptions.domain_exceptions import (
    ForbiddenError,
    NotFoundError,
)


def _make_task_list(owner_id: uuid.UUID | None = None) -> TaskList:
    return TaskList(
        id=uuid.uuid4(),
        name="My List",
        owner_id=owner_id or uuid.uuid4(),
        description="desc",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def repo() -> AsyncMock:
    return AsyncMock()


# ── CreateTaskListUseCase ────────────────────────────────────────────────────


async def test_create_task_list_returns_output(repo: AsyncMock) -> None:
    owner_id = uuid.uuid4()
    task_list = _make_task_list(owner_id)
    repo.create.return_value = task_list

    result = await CreateTaskListUseCase(repo).execute(
        CreateTaskListInput(name="My List", owner_id=owner_id)
    )

    assert result.name == "My List"
    assert result.owner_id == owner_id
    repo.create.assert_called_once()


# ── GetTaskListUseCase ───────────────────────────────────────────────────────


async def test_get_task_list_not_found_raises(repo: AsyncMock) -> None:
    repo.get_by_id.return_value = None
    with pytest.raises(NotFoundError):
        await GetTaskListUseCase(repo).execute(
            task_list_id=uuid.uuid4(), requester_id=uuid.uuid4()
        )


async def test_get_task_list_wrong_owner_raises(repo: AsyncMock) -> None:
    task_list = _make_task_list()
    repo.get_by_id.return_value = task_list
    with pytest.raises(ForbiddenError):
        await GetTaskListUseCase(repo).execute(
            task_list_id=task_list.id, requester_id=uuid.uuid4()
        )


async def test_get_task_list_success(repo: AsyncMock) -> None:
    owner_id = uuid.uuid4()
    task_list = _make_task_list(owner_id)
    repo.get_by_id.return_value = task_list

    result = await GetTaskListUseCase(repo).execute(
        task_list_id=task_list.id, requester_id=owner_id
    )
    assert result.id == task_list.id


# ── UpdateTaskListUseCase ────────────────────────────────────────────────────


async def test_update_task_list_changes_name(repo: AsyncMock) -> None:
    owner_id = uuid.uuid4()
    task_list = _make_task_list(owner_id)
    updated = TaskList(
        id=task_list.id,
        name="New name",
        owner_id=owner_id,
        description=task_list.description,
        created_at=task_list.created_at,
        updated_at=datetime.now(UTC),
    )
    repo.get_by_id.return_value = task_list
    repo.update.return_value = updated

    result = await UpdateTaskListUseCase(repo).execute(
        task_list_id=task_list.id,
        input_data=UpdateTaskListInput(name="New name"),
        requester_id=owner_id,
    )
    assert result.name == "New name"


# ── DeleteTaskListUseCase ────────────────────────────────────────────────────


async def test_delete_task_list_calls_repo(repo: AsyncMock) -> None:
    owner_id = uuid.uuid4()
    task_list = _make_task_list(owner_id)
    repo.get_by_id.return_value = task_list

    await DeleteTaskListUseCase(repo).execute(
        task_list_id=task_list.id, requester_id=owner_id
    )
    repo.delete.assert_called_once_with(task_list.id)


async def test_delete_task_list_forbidden(repo: AsyncMock) -> None:
    task_list = _make_task_list()
    repo.get_by_id.return_value = task_list
    with pytest.raises(ForbiddenError):
        await DeleteTaskListUseCase(repo).execute(
            task_list_id=task_list.id, requester_id=uuid.uuid4()
        )


# ── ListTaskListsUseCase ─────────────────────────────────────────────────────


async def test_list_task_lists_returns_all(repo: AsyncMock) -> None:
    owner_id = uuid.uuid4()
    lists = [_make_task_list(owner_id), _make_task_list(owner_id)]
    repo.get_all_by_owner.return_value = lists

    result = await ListTaskListsUseCase(repo).execute(owner_id=owner_id)

    assert len(result) == 2
    assert all(tl.owner_id == owner_id for tl in result)
    repo.get_all_by_owner.assert_called_once_with(owner_id)


async def test_list_task_lists_empty(repo: AsyncMock) -> None:
    repo.get_all_by_owner.return_value = []
    result = await ListTaskListsUseCase(repo).execute(owner_id=uuid.uuid4())
    assert result == []
