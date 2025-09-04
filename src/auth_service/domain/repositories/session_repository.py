from abc import ABC, abstractmethod
from typing import List, Optional

from auth_service.domain.value_objects.jti import JTI
from auth_service.domain.value_objects.session import Session
from auth_service.domain.value_objects.user_id import UserId


class AbstractSessionRepository(ABC):
    @abstractmethod
    async def add(self, session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_session(self, jti: JTI) -> Optional[Session]:
        raise NotImplementedError

    @abstractmethod
    async def get_sessions_by_user_id(self, user_id: UserId) -> List[Session]:
        raise NotImplementedError

    @abstractmethod
    async def revoke_session(self, jti: JTI) -> None:
        raise NotImplementedError

    @abstractmethod
    async def revoke_all_sessions(self, user_id: UserId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def is_active(self, jti: JTI) -> bool:
        raise NotImplementedError
