from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Optional
from uuid import uuid4

from auth_service.domain.value_objects import JTI, SessionID, UserID


@dataclass(slots=True)
class Session:
    id: SessionID
    user_id: UserID
    jti: JTI
    created_at: datetime
    expires_at: datetime
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    revoked_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        user_id: UserID,
        jti: JTI,
        created_at: datetime,
        expires_at: datetime,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> "Session":
        return cls(
            id=SessionID(uuid4()),
            user_id=user_id,
            jti=jti,
            created_at=created_at,
            expires_at=expires_at,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @property
    def is_active(self) -> bool:
        return not self.revoked_at and datetime.now(tz=UTC) < self.expires_at

    def revoke(self, revoked_at: datetime) -> None:
        self.revoked_at = revoked_at
