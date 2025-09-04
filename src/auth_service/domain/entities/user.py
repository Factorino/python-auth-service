from dataclasses import dataclass, field
from datetime import datetime, timezone

from auth_service.domain.value_objects import UserId, Username


@dataclass
class User:
    id: UserId
    username: Username
    hashed_password: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def verify_password(self, plain_password: str, bcrypt) -> bool:
        return bcrypt.checkpw(plain_password.encode(), self.hashed_password.encode())
