from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.auth_dtos import LoginInput, RegisterUserInput
from src.application.services.auth_service import AuthService
from src.application.use_cases.auth.login_user import LoginUserUseCase
from src.application.use_cases.auth.register_user import RegisterUserUseCase
from src.infrastructure.api.dependencies import get_auth_service, get_db
from src.infrastructure.api.schemas.auth_schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from src.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    body: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    use_case = RegisterUserUseCase(SQLAlchemyUserRepository(db), auth_service)
    result = await use_case.execute(
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
    db: Annotated[AsyncSession, Depends(get_db)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    use_case = LoginUserUseCase(SQLAlchemyUserRepository(db), auth_service)
    result = await use_case.execute(
        LoginInput(email=body.email, password=body.password)
    )
    return TokenResponse(access_token=result.access_token)
