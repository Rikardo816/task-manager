from src.application.dtos.auth_dtos import RegisterUserInput, RegisterUserOutput
from src.application.services.auth_service import AuthService
from src.domain.entities.user import User
from src.domain.exceptions.domain_exceptions import AlreadyExistsError
from src.domain.repositories.user_repository import UserRepository


class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepository, auth_service: AuthService) -> None:
        self._user_repo = user_repo
        self._auth_service = auth_service

    async def execute(self, input_data: RegisterUserInput) -> RegisterUserOutput:
        if await self._user_repo.get_by_email(input_data.email):
            raise AlreadyExistsError("User", "email", input_data.email)

        user = User(
            email=input_data.email,
            username=input_data.username,
            hashed_password=self._auth_service.hash_password(input_data.password),
        )
        created = await self._user_repo.create(user)
        return RegisterUserOutput(
            id=created.id,
            email=created.email,
            username=created.username,
        )
