from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions.domain_exceptions import NotFoundError
from src.infrastructure.api.dependencies import get_current_user_id, get_db
from src.infrastructure.api.schemas.auth_schemas import UserResponse
from src.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    user = await SQLAlchemyUserRepository(db).get_by_id(user_id)
    if not user:
        raise NotFoundError("User", str(user_id))
    return UserResponse(id=user.id, email=user.email, username=user.username)


@router.get("", response_model=list[UserResponse])
async def list_users(
    _: Annotated[UUID, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[UserResponse]:
    users = await SQLAlchemyUserRepository(db).get_all()
    return [UserResponse(id=u.id, email=u.email, username=u.username) for u in users]
