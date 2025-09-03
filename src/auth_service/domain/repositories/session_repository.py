from abc import ABC, abstractmethod

from auth_service.domain.value_objects.jti import JTI
from auth_service.domain.value_objects.user_id import UserId


class SessionRepository(ABC):
    @abstractmethod
    async def store_jti(self, jti: JTI, user_id: UserId, expires_in: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def is_jti_active(self, jti: JTI) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def revoke_jti(self, jti: JTI) -> None:
        raise NotImplementedError
