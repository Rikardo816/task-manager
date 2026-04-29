from httpx import AsyncClient


async def test_list_task_lists_empty(client: AsyncClient, auth_headers: dict) -> None:
    resp = await client.get("/task-lists", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_task_list(client: AsyncClient, auth_headers: dict) -> None:
    resp = await client.post(
        "/task-lists",
        json={"name": "Work", "description": "Work tasks"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Work"
    assert "id" in data


async def test_get_task_list(client: AsyncClient, auth_headers: dict) -> None:
    created = (
        await client.post(
            "/task-lists", json={"name": "Personal"}, headers=auth_headers
        )
    ).json()

    resp = await client.get(f"/task-lists/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


async def test_get_task_list_not_found(client: AsyncClient, auth_headers: dict) -> None:
    resp = await client.get(
        "/task-lists/00000000-0000-0000-0000-000000000000", headers=auth_headers
    )
    assert resp.status_code == 404


async def test_update_task_list(client: AsyncClient, auth_headers: dict) -> None:
    created = (
        await client.post(
            "/task-lists", json={"name": "Old name"}, headers=auth_headers
        )
    ).json()

    resp = await client.put(
        f"/task-lists/{created['id']}",
        json={"name": "New name"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New name"


async def test_delete_task_list(client: AsyncClient, auth_headers: dict) -> None:
    created = (
        await client.post(
            "/task-lists", json={"name": "To delete"}, headers=auth_headers
        )
    ).json()

    resp = await client.delete(f"/task-lists/{created['id']}", headers=auth_headers)
    assert resp.status_code == 204

    resp = await client.get(f"/task-lists/{created['id']}", headers=auth_headers)
    assert resp.status_code == 404


async def test_task_list_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/task-lists")
    assert resp.status_code == 401
