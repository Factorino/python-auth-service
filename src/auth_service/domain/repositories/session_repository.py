from abc import ABC, abstractmethod

from auth_service.domain.value_objects import JTI, UserId


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
