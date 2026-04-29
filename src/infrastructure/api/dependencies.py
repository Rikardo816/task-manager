from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.auth_service import AuthService
from src.config import get_settings
from src.infrastructure.database.connection import async_session_factory

_security = HTTPBearer()
_settings = get_settings()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_auth_service() -> AuthService:
    return AuthService(
        secret_key=_settings.SECRET_KEY,
        algorithm=_settings.ALGORITHM,
        expire_minutes=_settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UUID:
    payload = auth_service.decode_token(credentials.credentials)
    return UUID(payload["sub"])
