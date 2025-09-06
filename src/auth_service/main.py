import uuid
from dataclasses import dataclass

from adaptix.conversion import coercer, get_converter
from sqlalchemy import UUID, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from auth_service.infrastructure.redis.session_repository import Retort


@dataclass(frozen=True)
class UserId:
    value: uuid.UUID

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class User:
    id: UserId
    username: str


class BaseORM(DeclarativeBase):
    pass


class UserORM(BaseORM):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(
        String(30), unique=True, index=True, nullable=False
    )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.id=}, {self.username=})"


to_domain = get_converter(
    src=UserORM,
    dst=User,
    recipe=[
        coercer(uuid.UUID, UserId, lambda uuid: UserId(uuid)),
    ],
)

to_orm = get_converter(
    src=User,
    dst=UserORM,
    recipe=[
        coercer(UserId, uuid.UUID, lambda user_id: user_id.value),
    ],
)

id = uuid.uuid4()
username = "user"

user = User(UserId(id), username)

# print(user)

user_orm = UserORM(id=id, username=username)
# print(user_orm)
