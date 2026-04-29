from uuid import UUID

from src.application.dtos.user_dtos import UserOutput
from src.domain.exceptions.domain_exceptions import NotFoundError
from src.domain.repositories.user_repository import UserRepository


class GetUserUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self, user_id: UUID) -> UserOutput:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        return UserOutput(id=user.id, email=user.email, username=user.username)
