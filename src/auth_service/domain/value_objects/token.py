from dataclasses import dataclass
from datetime import datetime

from auth_service.domain.value_objects import JTI, TokenType, UserID


@dataclass(frozen=True, slots=True)
class Token:
    jti: JTI
    user_id: UserID
    expires_at: datetime
    type: TokenType
