from src.application.dtos.user_dtos import UserOutput
from src.domain.repositories.user_repository import UserRepository


class ListUsersUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def execute(self) -> list[UserOutput]:
        users = await self._user_repo.get_all()
        return [UserOutput(id=u.id, email=u.email, username=u.username) for u in users]
