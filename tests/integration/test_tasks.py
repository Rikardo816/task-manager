import pytest
from httpx import AsyncClient


@pytest.fixture
async def task_list(client: AsyncClient, auth_headers: dict) -> dict:
    resp = await client.post(
        "/task-lists",
        json={"name": "Sprint 1"},
        headers=auth_headers,
    )
    return resp.json()


async def test_create_task(
    client: AsyncClient, auth_headers: dict, task_list: dict
) -> None:
    resp = await client.post(
        f"/task-lists/{task_list['id']}/tasks",
        json={"title": "Implement feature X", "priority": "high"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Implement feature X"
    assert data["status"] == "todo"
    assert data["priority"] == "high"


async def test_list_tasks_with_completion(
    client: AsyncClient, auth_headers: dict, task_list: dict
) -> None:
    tl_id = task_list["id"]
    t1 = (
        await client.post(
            f"/task-lists/{tl_id}/tasks",
            json={"title": "Task 1"},
            headers=auth_headers,
        )
    ).json()
    await client.post(
        f"/task-lists/{tl_id}/tasks",
        json={"title": "Task 2"},
        headers=auth_headers,
    )

    await client.patch(
        f"/task-lists/{tl_id}/tasks/{t1['id']}/status",
        json={"status": "done"},
        headers=auth_headers,
    )

    resp = await client.get(f"/task-lists/{tl_id}/tasks", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_tasks"] == 2
    assert data["completed_tasks"] == 1
    assert data["completion_percentage"] == 50.0


async def test_filter_tasks_by_status(
    client: AsyncClient, auth_headers: dict, task_list: dict
) -> None:
    tl_id = task_list["id"]
    t = (
        await client.post(
            f"/task-lists/{tl_id}/tasks",
            json={"title": "Filter me"},
            headers=auth_headers,
        )
    ).json()
    await client.patch(
        f"/task-lists/{tl_id}/tasks/{t['id']}/status",
        json={"status": "in_progress"},
        headers=auth_headers,
    )

    resp = await client.get(
        f"/task-lists/{tl_id}/tasks?status=in_progress", headers=auth_headers
    )
    assert resp.status_code == 200
    tasks = resp.json()["tasks"]
    assert all(t["status"] == "in_progress" for t in tasks)


async def test_filter_tasks_by_priority(
    client: AsyncClient, auth_headers: dict, task_list: dict
) -> None:
    tl_id = task_list["id"]
    await client.post(
        f"/task-lists/{tl_id}/tasks",
        json={"title": "High prio", "priority": "high"},
        headers=auth_headers,
    )
    await client.post(
        f"/task-lists/{tl_id}/tasks",
        json={"title": "Low prio", "priority": "low"},
        headers=auth_headers,
    )

    resp = await client.get(
        f"/task-lists/{tl_id}/tasks?priority=high", headers=auth_headers
    )
    tasks = resp.json()["tasks"]
    assert all(t["priority"] == "high" for t in tasks)


async def test_change_task_status(
    client: AsyncClient, auth_headers: dict, task_list: dict
) -> None:
    tl_id = task_list["id"]
    task = (
        await client.post(
            f"/task-lists/{tl_id}/tasks",
            json={"title": "Status test"},
            headers=auth_headers,
        )
    ).json()

    resp = await client.patch(
        f"/task-lists/{tl_id}/tasks/{task['id']}/status",
        json={"status": "done"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"


async def test_update_task(
    client: AsyncClient, auth_headers: dict, task_list: dict
) -> None:
    tl_id = task_list["id"]
    task = (
        await client.post(
            f"/task-lists/{tl_id}/tasks",
            json={"title": "Old title"},
            headers=auth_headers,
        )
    ).json()

    resp = await client.put(
        f"/task-lists/{tl_id}/tasks/{task['id']}",
        json={"title": "New title", "priority": "low"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "New title"


async def test_delete_task(
    client: AsyncClient, auth_headers: dict, task_list: dict
) -> None:
    tl_id = task_list["id"]
    task = (
        await client.post(
            f"/task-lists/{tl_id}/tasks",
            json={"title": "To delete"},
            headers=auth_headers,
        )
    ).json()

    resp = await client.delete(
        f"/task-lists/{tl_id}/tasks/{task['id']}", headers=auth_headers
    )
    assert resp.status_code == 204

    resp = await client.get(
        f"/task-lists/{tl_id}/tasks/{task['id']}", headers=auth_headers
    )
    assert resp.status_code == 404


async def test_get_task_not_found(
    client: AsyncClient, auth_headers: dict, task_list: dict
) -> None:
    tl_id = task_list["id"]
    resp = await client.get(
        f"/task-lists/{tl_id}/tasks/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert resp.status_code == 404
