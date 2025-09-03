from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from auth_service.domain.value_objects.jti import JTI
from auth_service.domain.value_objects.token_type import TokenType
from auth_service.domain.value_objects.user_id import UserId


@dataclass(frozen=True)
class JWTPayload:
    sub: UserId
    jti: JTI
    type: TokenType
    exp: datetime
    iat: datetime
    additional_claims: Dict[str, Any] = None  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "sub": int(self.sub),
            "jti": str(self.jti),
            "type": self.type,
            "exp": self.exp.timestamp(),
            "iat": self.iat.timestamp(),
        }
        if self.additional_claims:
            payload.update(self.additional_claims)
        return payload
