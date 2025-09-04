from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from auth_service.domain.value_objects import JTI, UserId


@dataclass(frozen=True)
class Session:
    jti: JTI
    user_id: UserId
    created_at: datetime
    expires_at: datetime
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_revoked: bool = False

    def is_active(self) -> bool:
        return not self.is_revoked and datetime.now(timezone.utc) < self.expires_at
