from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.application.use_cases.user.get_user import GetUserUseCase
from src.application.use_cases.user.list_users import ListUsersUseCase
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.api.dependencies import get_current_user_id, get_user_repo
from src.infrastructure.api.schemas.auth_schemas import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> UserResponse:
    result = await GetUserUseCase(user_repo).execute(user_id)
    return UserResponse(id=result.id, email=result.email, username=result.username)


@router.get("", response_model=list[UserResponse])
async def list_users(
    _: Annotated[UUID, Depends(get_current_user_id)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> list[UserResponse]:
    results = await ListUsersUseCase(user_repo).execute()
    return [UserResponse(id=u.id, email=u.email, username=u.username) for u in results]
