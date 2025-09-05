from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from auth_service.domain.value_objects import UserStatus


@dataclass(frozen=True, slots=True)
class UserFilters:
    username: Optional[str] = None
    status: Optional[UserStatus] = None
    created_at__gte: Optional[datetime] = None
    created_at__lte: Optional[datetime] = None
    updated_at__gte: Optional[datetime] = None
    updated_at__lte: Optional[datetime] = None
    revoked_at__gte: Optional[datetime] = None
    revoked_at__lte: Optional[datetime] = None
