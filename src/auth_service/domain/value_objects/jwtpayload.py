from dataclasses import dataclass
from datetime import datetime

from auth_service.domain.value_objects.jti import JTI
from auth_service.domain.value_objects.token_type import TokenType
from auth_service.domain.value_objects.user_id import UserID


@dataclass(frozen=True)
class JWTPayload:
    sub: UserID
    jti: JTI
    type: TokenType
    exp: datetime
    iat: datetime
