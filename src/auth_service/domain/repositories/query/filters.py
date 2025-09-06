from dataclasses import dataclass, fields
from datetime import datetime
from typing import Any, Dict, Optional

from auth_service.domain.value_objects.user_status import UserStatus


@dataclass(frozen=True, slots=True)
class BaseFilters:
    def to_dict(self, exclude_none=False) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for field in fields(self.__class__):
            value = getattr(self, field.name)
            if exclude_none and value is None:
                continue
            result[field.name] = value
        return result


@dataclass(frozen=True, slots=True)
class UserFilters(BaseFilters):
    username: Optional[str] = None
    status: Optional[UserStatus] = None
    created_at__gte: Optional[datetime] = None
    created_at__lte: Optional[datetime] = None
    updated_at__gte: Optional[datetime] = None
    updated_at__lte: Optional[datetime] = None
    revoked_at__gte: Optional[datetime] = None
    revoked_at__lte: Optional[datetime] = None
