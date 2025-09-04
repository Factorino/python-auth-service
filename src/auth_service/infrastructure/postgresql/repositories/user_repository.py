from typing import Optional, Tuple

from sqlalchemy import Result, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from auth_service.domain.entities import User
from auth_service.domain.repositories import AbstractUserRepository
from auth_service.domain.value_objects import UserID, Username
from auth_service.infrastructure.postgresql.database.models import UserDB


class SQLAlchemyUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def add(self, user: User) -> User:
        user_db = UserDB(
            id=user.id.value,
            username=user.username.value,
            hashed_password=user.hashed_password,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        self._session.add(user_db)
        await self._session.flush()
        return user

    async def get_by_id(self, user_id: UserID) -> Optional[User]:
        result: Result[Tuple[UserDB]] = await self._session.execute(
            select(UserDB).where(UserDB.id == user_id.value)
        )
        user_db: Optional[UserDB] = result.scalar()
        return self._to_entity(user_db) if user_db else None

    async def get_by_username(self, username: Username) -> Optional[User]:
        result: Result[Tuple[UserDB]] = await self._session.execute(
            select(UserDB).where(UserDB.username == username.value)
        )
        user_db: Optional[UserDB] = result.scalar()
        return self._to_entity(user_db) if user_db else None

    async def exists_by_username(self, username: Username) -> bool:
        stmt: Select[Tuple[bool]] = select(
            exists().where(UserDB.username == username.value)
        )
        result: Result[Tuple[bool]] = await self._session.execute(stmt)
        return result.scalar_one()

    def _to_entity(self, user_db: UserDB) -> User:
        return User(
            id=UserID(user_db.id),
            username=Username(user_db.username),
            hashed_password=user_db.hashed_password,
            created_at=user_db.created_at,
            updated_at=user_db.updated_at,
        )
