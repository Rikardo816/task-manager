from src.application.dtos.auth_dtos import LoginInput, LoginOutput
from src.application.services.auth_service import AuthService
from src.domain.exceptions.domain_exceptions import UnauthorizedError
from src.domain.repositories.user_repository import UserRepository


class LoginUserUseCase:
    def __init__(self, user_repo: UserRepository, auth_service: AuthService) -> None:
        self._user_repo = user_repo
        self._auth_service = auth_service

    _DUMMY_HASH = "$2b$12$QoRCezPpBBVnKYhQlnBPpemqD3DLzVHoHyUTkrGCbBjXZAHuMoJPm"

    async def execute(self, input_data: LoginInput) -> LoginOutput:
        user = await self._user_repo.get_by_email(input_data.email)

        if not user or not user.is_active:
            # Run dummy verify to prevent timing-based user enumeration
            self._auth_service.verify_password(input_data.password, self._DUMMY_HASH)
            raise UnauthorizedError("Invalid credentials")

        if not self._auth_service.verify_password(
            input_data.password, user.hashed_password
        ):
            raise UnauthorizedError("Invalid credentials")

        token = self._auth_service.create_access_token(
            user.id, user.email, user.username
        )
        return LoginOutput(access_token=token)
