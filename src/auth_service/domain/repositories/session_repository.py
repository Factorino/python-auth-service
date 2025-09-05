from abc import ABC, abstractmethod
from typing import List, Optional

from auth_service.domain.entities import Session
from auth_service.domain.value_objects import JTI, SessionID, UserID


class AbstractSessionRepository(ABC):
    @abstractmethod
    async def get_all_by_user_id(self, user_id: UserID) -> List[Session]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, session_id: SessionID) -> Optional[Session]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_jti(self, jti: JTI) -> Optional[Session]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, session: Session) -> Session:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, jti: JTI) -> Session:
        raise NotImplementedError
