from abc import ABC, abstractmethod
from typing import Optional

from auth_service.domain.entities import User
from auth_service.domain.value_objects import UserId, Username


class AbstractUserRepository(ABC):
    @abstractmethod
    async def add(self, user: User) -> User:
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: Username) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_username(self, username: Username) -> bool:
        raise NotImplementedError
