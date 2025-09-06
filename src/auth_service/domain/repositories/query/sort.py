from dataclasses import dataclass
from enum import StrEnum
from typing import Generic, TypeVar

SortField = TypeVar("SortField", bound=StrEnum)


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True, slots=True)
class SortBy(Generic[SortField]):
    field: SortField
    direction: SortDirection = SortDirection.ASC


class UserSortField(StrEnum):
    USERNAME = "username"
    STATUS = "status"
    CREATED_AT = "created_at"
