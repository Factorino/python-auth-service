from abc import ABC, abstractmethod

from auth_service.domain.value_objects.jti import JTI
from auth_service.domain.value_objects.jwtpayload import JWTPayload
from auth_service.domain.value_objects.user_id import UserID


class AbstractJWTService(ABC):
    @abstractmethod
    def create_access_token(self, user_id: UserID, jti: JTI) -> str:
        raise NotImplementedError

    @abstractmethod
    def create_refresh_token(self, user_id: UserID, jti: JTI) -> str:
        raise NotImplementedError

    @abstractmethod
    async def decode_token(self, token: str) -> JWTPayload:
        raise NotImplementedError
