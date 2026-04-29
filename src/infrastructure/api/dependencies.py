from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.auth_service import AuthService
from src.config import get_settings
from src.domain.repositories.task_list_repository import TaskListRepository
from src.domain.repositories.task_repository import TaskRepository
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.connection import async_session_factory
from src.infrastructure.repositories.sqlalchemy_task_list_repository import (
    SQLAlchemyTaskListRepository,
)
from src.infrastructure.repositories.sqlalchemy_task_repository import (
    SQLAlchemyTaskRepository,
)
from src.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

_security = HTTPBearer()
_settings = get_settings()

_auth_service = AuthService(
    secret_key=_settings.SECRET_KEY,
    algorithm=_settings.ALGORITHM,
    expire_minutes=_settings.ACCESS_TOKEN_EXPIRE_MINUTES,
)


@dataclass(frozen=True)
class CurrentUser:
    id: UUID
    username: str


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_auth_service() -> AuthService:
    return _auth_service


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_security)],
) -> CurrentUser:
    payload = _auth_service.decode_token(credentials.credentials)
    return CurrentUser(
        id=UUID(str(payload["sub"])),
        username=str(payload.get("username", "")),
    )


async def get_current_user_id(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> UUID:
    return current_user.id


def get_task_repo(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskRepository:
    return SQLAlchemyTaskRepository(db)


def get_task_list_repo(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskListRepository:
    return SQLAlchemyTaskListRepository(db)


def get_user_repo(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRepository:
    return SQLAlchemyUserRepository(db)
