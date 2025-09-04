from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Optional
from uuid import uuid4

from auth_service.domain.value_objects import UserID, Username, UserStatus


@dataclass(slots=True)
class User:
    id: UserID
    username: Username
    password_hash: str
    created_at: datetime
    updated_at: datetime
    revoked_at: Optional[datetime] = None
    status: UserStatus = UserStatus.ACTIVE

    @classmethod
    def create(
        cls,
        username: Username,
        password_hash: str,
        created_at: datetime,
    ) -> "User":
        return cls(
            id=UserID(uuid4()),
            username=username,
            password_hash=password_hash,
            created_at=created_at,
            updated_at=created_at,
        )

    def update_username(self, username: Username) -> None:
        self.username = username
        self.updated_at = datetime.now(tz=UTC)

    def block(self, revoked_at: datetime) -> None:
        self.status = UserStatus.BLOCKED
        self.revoked_at = revoked_at
        self.updated_at = revoked_at

    def activate(self, updated_at: datetime) -> None:
        self.status = UserStatus.ACTIVE
        self.revoked_at = None
        self.updated_at = updated_at
