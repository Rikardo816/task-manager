import uuid
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.application.dtos.task_dtos import CreateTaskInput, ListTasksInput
from src.application.use_cases.task.change_task_status import ChangeTaskStatusUseCase
from src.application.use_cases.task.create_task import CreateTaskUseCase
from src.application.use_cases.task.list_tasks import ListTasksUseCase
from src.domain.entities.task import Task
from src.domain.entities.task_list import TaskList
from src.domain.exceptions.domain_exceptions import ForbiddenError, NotFoundError
from src.domain.value_objects.enums import Priority, TaskStatus


def _make_task_list(owner_id: uuid.UUID) -> TaskList:
    return TaskList(
        id=uuid.uuid4(),
        name="List",
        owner_id=owner_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


def _make_task(task_list_id: uuid.UUID, status: TaskStatus = TaskStatus.TODO) -> Task:
    return Task(
        id=uuid.uuid4(),
        title="Do something",
        task_list_id=task_list_id,
        status=status,
        priority=Priority.MEDIUM,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def task_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def task_list_repo() -> AsyncMock:
    return AsyncMock()


# ── CreateTaskUseCase ────────────────────────────────────────────────────────


async def test_create_task_success(
    task_repo: AsyncMock, task_list_repo: AsyncMock
) -> None:
    owner_id = uuid.uuid4()
    task_list = _make_task_list(owner_id)
    task = _make_task(task_list.id)

    task_list_repo.get_by_id.return_value = task_list
    task_repo.create.return_value = task

    result = await CreateTaskUseCase(task_repo, task_list_repo).execute(
        CreateTaskInput(title="Do something", task_list_id=task_list.id),
        requester_id=owner_id,
    )
    assert result.title == "Do something"
    assert result.status == TaskStatus.TODO


async def test_create_task_list_not_found(
    task_repo: AsyncMock, task_list_repo: AsyncMock
) -> None:
    task_list_repo.get_by_id.return_value = None
    with pytest.raises(NotFoundError):
        await CreateTaskUseCase(task_repo, task_list_repo).execute(
            CreateTaskInput(title="X", task_list_id=uuid.uuid4()),
            requester_id=uuid.uuid4(),
        )


async def test_create_task_forbidden(
    task_repo: AsyncMock, task_list_repo: AsyncMock
) -> None:
    task_list = _make_task_list(uuid.uuid4())
    task_list_repo.get_by_id.return_value = task_list
    with pytest.raises(ForbiddenError):
        await CreateTaskUseCase(task_repo, task_list_repo).execute(
            CreateTaskInput(title="X", task_list_id=task_list.id),
            requester_id=uuid.uuid4(),
        )


# ── ListTasksUseCase ─────────────────────────────────────────────────────────


async def test_list_tasks_completion_percentage(
    task_repo: AsyncMock, task_list_repo: AsyncMock
) -> None:
    owner_id = uuid.uuid4()
    task_list = _make_task_list(owner_id)
    tasks = [
        _make_task(task_list.id, TaskStatus.DONE),
        _make_task(task_list.id, TaskStatus.DONE),
        _make_task(task_list.id, TaskStatus.TODO),
        _make_task(task_list.id, TaskStatus.IN_PROGRESS),
    ]

    task_list_repo.get_by_id.return_value = task_list
    task_repo.count_by_task_list.return_value = 4
    task_repo.count_completed_by_task_list.return_value = 2
    task_repo.get_all_by_task_list.return_value = tasks

    result = await ListTasksUseCase(task_repo, task_list_repo).execute(
        ListTasksInput(task_list_id=task_list.id), requester_id=owner_id
    )

    assert result.completion_percentage == 50.0
    assert result.total_tasks == 4
    assert result.completed_tasks == 2


async def test_list_tasks_empty_list_zero_percentage(
    task_repo: AsyncMock, task_list_repo: AsyncMock
) -> None:
    owner_id = uuid.uuid4()
    task_list = _make_task_list(owner_id)
    task_list_repo.get_by_id.return_value = task_list
    task_repo.count_by_task_list.return_value = 0
    task_repo.count_completed_by_task_list.return_value = 0
    task_repo.get_all_by_task_list.return_value = []

    result = await ListTasksUseCase(task_repo, task_list_repo).execute(
        ListTasksInput(task_list_id=task_list.id), requester_id=owner_id
    )
    assert result.completion_percentage == 0.0


# ── ChangeTaskStatusUseCase ──────────────────────────────────────────────────


async def test_change_task_status(
    task_repo: AsyncMock, task_list_repo: AsyncMock
) -> None:
    owner_id = uuid.uuid4()
    task_list = _make_task_list(owner_id)
    task = _make_task(task_list.id)
    changed = Task(
        id=task.id,
        title=task.title,
        task_list_id=task.task_list_id,
        status=TaskStatus.DONE,
        priority=task.priority,
        created_at=task.created_at,
        updated_at=datetime.utcnow(),
    )

    task_list_repo.get_by_id.return_value = task_list
    task_repo.get_by_id.return_value = task
    task_repo.update.return_value = changed

    result = await ChangeTaskStatusUseCase(task_repo, task_list_repo).execute(
        task_id=task.id,
        task_list_id=task_list.id,
        new_status=TaskStatus.DONE,
        requester_id=owner_id,
    )
    assert result.status == TaskStatus.DONE
