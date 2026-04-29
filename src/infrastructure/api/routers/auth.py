from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.application.dtos.auth_dtos import LoginInput, RegisterUserInput
from src.application.services.auth_service import AuthService
from src.application.use_cases.auth.login_user import LoginUserUseCase
from src.application.use_cases.auth.register_user import RegisterUserUseCase
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.api.dependencies import get_auth_service, get_user_repo
from src.infrastructure.api.schemas.auth_schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    body: RegisterRequest,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    result = await RegisterUserUseCase(user_repo, auth_service).execute(
        RegisterUserInput(
            email=body.email,
            username=body.username,
            password=body.password,
        )
    )
    return UserResponse(id=result.id, email=result.email, username=result.username)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    result = await LoginUserUseCase(user_repo, auth_service).execute(
        LoginInput(email=body.email, password=body.password)
    )
    return TokenResponse(access_token=result.access_token)
