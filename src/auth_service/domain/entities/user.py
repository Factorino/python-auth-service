from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from auth_service.domain.value_objects.user_id import UserId
from auth_service.domain.value_objects.username import Username


@dataclass
class User:
    id: UserId
    username: Username
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    def verify_password(self, plain_password: str, bcrypt) -> bool:
        return bcrypt.checkpw(plain_password.encode(), self.hashed_password.encode())
