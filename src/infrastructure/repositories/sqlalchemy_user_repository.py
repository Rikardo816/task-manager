from uuid import UUID

from sqlalchemy import select
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models.user_model import UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, m: UserModel) -> User:
        return User(
            id=m.id,
            email=m.email,
            username=m.username,
            hashed_password=m.hashed_password,
            is_active=m.is_active,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    async def get_by_id(self, user_id: UUID) -> User | None:
        row = await self._session.scalar(
            select(UserModel).where(UserModel.id == user_id)
        )
        return self._to_entity(row) if row else None

    async def get_by_email(self, email: str) -> User | None:
        row = await self._session.scalar(
            select(UserModel).where(UserModel.email == email)
        )
        return self._to_entity(row) if row else None

    async def get_all(self) -> list[User]:
        rows = await self._session.scalars(select(UserModel))
        return [self._to_entity(r) for r in rows]

    async def create(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            email=user.email,
            username=user.username,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, user: User) -> User:
        await self._session.execute(
            sa_update(UserModel)
            .where(UserModel.id == user.id)
            .values(
                email=user.email,
                username=user.username,
                hashed_password=user.hashed_password,
                is_active=user.is_active,
                updated_at=user.updated_at,
            )
        )
        await self._session.flush()
        return user
