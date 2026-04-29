import uuid

import pytest

from src.domain.entities.task import Task
from src.domain.value_objects.enums import Priority, TaskStatus


@pytest.fixture
def task() -> Task:
    return Task(title="Test task", task_list_id=uuid.uuid4())


def test_task_defaults(task: Task) -> None:
    assert task.status == TaskStatus.TODO
    assert task.priority == Priority.MEDIUM
    assert task.assignee_id is None
    assert task.due_date is None
    assert isinstance(task.id, uuid.UUID)


def test_change_status_updates_field(task: Task) -> None:
    before = task.updated_at
    task.change_status(TaskStatus.IN_PROGRESS)
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.updated_at >= before


def test_change_status_to_done(task: Task) -> None:
    task.change_status(TaskStatus.DONE)
    assert task.status == TaskStatus.DONE


def test_assign_to_sets_assignee(task: Task) -> None:
    user_id = uuid.uuid4()
    before = task.updated_at
    task.assign_to(user_id)
    assert task.assignee_id == user_id
    assert task.updated_at >= before


def test_assign_to_can_reassign(task: Task) -> None:
    user_id_1 = uuid.uuid4()
    user_id_2 = uuid.uuid4()
    task.assign_to(user_id_1)
    task.assign_to(user_id_2)
    assert task.assignee_id == user_id_2


def test_task_unique_ids() -> None:
    t1 = Task(title="A", task_list_id=uuid.uuid4())
    t2 = Task(title="B", task_list_id=uuid.uuid4())
    assert t1.id != t2.id
