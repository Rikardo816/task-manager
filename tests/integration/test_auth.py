import pytest
from httpx import AsyncClient


@pytest.fixture
async def registered_user(client: AsyncClient) -> dict:
    resp = await client.post(
        "/auth/register",
        json={
            "email": "auth_test@example.com",
            "username": "authuser",
            "password": "password123",
        },
    )
    assert resp.status_code == 201
    return resp.json()


async def test_register_success(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/register",
        json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "password123",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "new@example.com"
    assert "id" in data


async def test_register_duplicate_email(client: AsyncClient) -> None:
    payload = {
        "email": "dup@example.com",
        "username": "dupuser",
        "password": "password123",
    }
    await client.post("/auth/register", json=payload)
    resp = await client.post("/auth/register", json=payload)
    assert resp.status_code == 409


async def test_register_invalid_email(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/register",
        json={"email": "not-an-email", "username": "user", "password": "password123"},
    )
    assert resp.status_code == 422


async def test_login_success(client: AsyncClient, registered_user: dict) -> None:
    resp = await client.post(
        "/auth/login",
        json={"email": "auth_test@example.com", "password": "password123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient, registered_user: dict) -> None:
    resp = await client.post(
        "/auth/login",
        json={"email": "auth_test@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401


async def test_login_unknown_email(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/login",
        json={"email": "ghost@example.com", "password": "password123"},
    )
    assert resp.status_code == 401
