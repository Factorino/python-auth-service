from abc import ABC, abstractmethod
from typing import Optional

from auth_service.domain.entities import User
from auth_service.domain.repositories.query import Pagination, QueryResult, SortBy, UserFilters, UserSortField
from auth_service.domain.value_objects import UserID, Username


class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_all(
        self,
        sort_by: Optional[SortBy[UserSortField]] = None,
        pagination: Optional[Pagination] = None,
    ) -> QueryResult[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_filtered(
        self,
        filters: UserFilters,
        sort_by: Optional[SortBy[UserSortField]] = None,
        pagination: Optional[Pagination] = None,
    ) -> QueryResult[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UserID) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: Username) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: UserID) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def count(
        self,
        filters: Optional[UserFilters],
    ) -> int:
        raise NotImplementedError
