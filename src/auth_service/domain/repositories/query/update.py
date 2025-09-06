from dataclasses import dataclass, fields
from datetime import datetime
from typing import Any, Dict, Optional

from auth_service.domain.value_objects.user_status import UserStatus


@dataclass(frozen=True, slots=True)
class BaseUpdate:
    def to_dict(self, exclude_none=False) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for field in fields(self.__class__):
            value: Any = getattr(self, field.name)
            if exclude_none and value is None:
                continue
            result[field.name] = value
        return result


@dataclass(frozen=True, slots=True)
class UserUpdate(BaseUpdate):
    username: Optional[str] = None
    password_hash: Optional[str] = None
    status: Optional[UserStatus] = None
    revoked_at: Optional[datetime] = None
