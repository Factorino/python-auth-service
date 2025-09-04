from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import List, Optional

from auth_service.domain.entities import User
from auth_service.domain.value_objects import UserID, Username, UserStatus


class UserSortBy(StrEnum):
    ID = "id"
    USERNAME = "username"
    STATUS = "status"
    CREATED_AT = "created_at"


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True, slots=True)
class SortBy:
    field: UserSortBy = UserSortBy.ID
    direction: SortDirection = SortDirection.ASC


@dataclass(frozen=True, slots=True)
class Pagination:
    page: int = 1
    page_size: int = 25

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


@dataclass(frozen=True, slots=True)
class QueryResult:
    items: List[User]
    total: int
    page: int
    page_size: int
    total_pages: int

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1


@dataclass(frozen=True, slots=True)
class UserFilters:
    username: Optional[str] = None
    status: Optional[UserStatus] = None
    created_at__gte: Optional[datetime] = None
    created_at__lte: Optional[datetime] = None
    updated_at__gte: Optional[datetime] = None
    updated_at__lte: Optional[datetime] = None
    revoked_at__gte: Optional[datetime] = None
    revoked_at__lte: Optional[datetime] = None


class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_all(
        self,
        sort_by: Optional[SortBy] = None,
        pagination: Optional[Pagination] = None,
    ) -> QueryResult:
        raise NotImplementedError

    @abstractmethod
    async def get_filtered(
        self,
        filters: UserFilters,
        sort_by: Optional[SortBy] = None,
        pagination: Optional[Pagination] = None,
    ) -> QueryResult:
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
