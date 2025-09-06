import uuid
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from adaptix.conversion import coercer, get_converter
from sqlalchemy import Result, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql import Select
from sqlalchemy.sql.dml import ReturningUpdate

from auth_service.domain.entities.user import User
from auth_service.domain.repositories.query.filters import UserFilters
from auth_service.domain.repositories.query.pagination import Pagination
from auth_service.domain.repositories.query.result import QueryResult
from auth_service.domain.repositories.query.sort import (
    SortBy,
    SortDirection,
    UserSortField,
)
from auth_service.domain.repositories.query.update import UserUpdate
from auth_service.domain.repositories.user_repository import AbstractUserRepository
from auth_service.domain.value_objects.user_id import UserID
from auth_service.domain.value_objects.username import Username
from auth_service.infrastructure.postgresql.models.user import UserORM


class SQLAlchemyUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session
        self._to_domain: Callable[[UserORM], User] = self._setup_to_domain_mapper()
        self._to_orm: Callable[[User], UserORM] = self._setup_to_orm_mapper()

    async def get_all(
        self,
        sort_by: Optional[SortBy[UserSortField]] = None,
        pagination: Optional[Pagination] = None,
    ) -> QueryResult[User]:
        # Get items with sorting and pagination
        query: Select[Tuple[UserORM]] = select(UserORM)
        query = self._apply_sorting(query, sort_by)
        query = self._apply_pagination(query, pagination)
        result: Result[Tuple[UserORM]] = await self._session.execute(query)
        orm_items: Sequence[UserORM] = result.scalars().all()
        # Convert ORM to Domain
        items: List[User] = [self._to_domain(orm_item) for orm_item in orm_items]

        # Count total with filters
        count_query: Select[Tuple[int]] = select(func.count()).select_from(UserORM)
        count_result: Result[Tuple[int]] = await self._session.execute(count_query)
        total: int = count_result.scalar_one()

        # Calculate page, page_size, total pages
        page: int = pagination.page if pagination else 1
        page_size: int = pagination.page_size if pagination else total
        total_pages: int = (total + page_size - 1) // page_size if page_size > 0 else 1

        return QueryResult(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_filtered(
        self,
        filters: UserFilters,
        sort_by: Optional[SortBy[UserSortField]] = None,
        pagination: Optional[Pagination] = None,
    ) -> QueryResult[User]:
        # Get items with filters, sorting and pagination
        query: Select[Tuple[UserORM]] = select(UserORM)
        query = self._apply_filters(query, filters)
        query = self._apply_sorting(query, sort_by)
        query = self._apply_pagination(query, pagination)
        result: Result[Tuple[UserORM]] = await self._session.execute(query)
        orm_items: Sequence[UserORM] = result.scalars().all()
        # Convert ORM to Domain
        items: List[User] = [self._to_domain(orm_item) for orm_item in orm_items]

        # Count total with filters
        count_query: Select[Tuple[int]] = select(func.count()).select_from(UserORM)
        count_query = self._apply_filters(count_query, filters)
        count_result: Result[Tuple[int]] = await self._session.execute(count_query)
        total: int = count_result.scalar_one()

        # Calculate page, page_size, total pages
        page: int = pagination.page if pagination else 1
        page_size: int = pagination.page_size if pagination else total
        total_pages: int = (total + page_size - 1) // page_size if page_size > 0 else 1

        return QueryResult(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_by_id(self, user_id: UserID) -> Optional[User]:
        query: Select[Tuple[UserORM]] = select(UserORM).where(
            UserORM.id == user_id.value
        )
        result: Result[Tuple[UserORM]] = await self._session.execute(query)
        user_orm: Optional[UserORM] = result.scalar_one_or_none()
        return self._to_domain(user_orm) if user_orm else None

    async def get_by_username(self, username: Username) -> Optional[User]:
        query: Select[Tuple[UserORM]] = select(UserORM).where(
            UserORM.username == str(username)
        )
        result: Result[Tuple[UserORM]] = await self._session.execute(query)
        user_orm: Optional[UserORM] = result.scalar_one_or_none()
        return self._to_domain(user_orm) if user_orm else None

    async def add(self, user: User) -> User:
        user_orm: UserORM = self._to_orm(user)
        self._session.add(user_orm)
        await self._session.flush()
        await self._session.refresh(user_orm)
        return self._to_domain(user_orm)

    async def update(self, id: UserID, data: UserUpdate) -> Optional[User]:
        update_data: Dict[str, Any] = data.to_dict(exclude_none=True)

        if not update_data:
            return await self.get_by_id(id)

        query: ReturningUpdate[Tuple[UserORM]] = (
            update(UserORM)
            .where(UserORM.id == id.value)
            .values(**update_data)
            .returning(UserORM)
        )

        result: Result[Tuple[UserORM]] = await self._session.execute(query)
        updated_orm: Optional[UserORM] = result.scalar_one_or_none()

        if not updated_orm:
            return None

        await self._session.flush()
        return self._to_domain(updated_orm)

    async def delete(self, user_id: UserID) -> Optional[User]:
        query: Select[Tuple[UserORM]] = select(UserORM).where(
            UserORM.id == user_id.value
        )
        result: Result[Tuple[UserORM]] = await self._session.execute(query)
        user_orm: Optional[UserORM] = result.scalar_one_or_none()

        if not user_orm:
            return None

        await self._session.delete(user_orm)
        await self._session.flush()
        return self._to_domain(user_orm)

    async def count(
        self,
        filters: Optional[UserFilters],
    ) -> int:
        query: Select[Tuple[int]] = select(func.count()).select_from(UserORM)
        query = self._apply_filters(query, filters)
        result: Result[Tuple[int]] = await self._session.execute(query)
        return result.scalar_one()

    def _apply_filters(self, query: Select, filters: Optional[UserFilters]) -> Select:
        if not filters:
            return query

        filter_dict: Dict[str, Any] = filters.to_dict(exclude_none=True)

        for field_name, value in filter_dict.items():
            # Process special suffixes __lte and __gte
            if field_name.endswith("__lte"):
                base_field_name: str = field_name[:-5]
                if hasattr(UserORM, base_field_name):
                    field: InstrumentedAttribute = getattr(UserORM, base_field_name)
                    query = query.where(field <= value)
                continue

            if field_name.endswith("__gte"):
                base_field_name = field_name[:-5]
                if hasattr(UserORM, base_field_name):
                    field: InstrumentedAttribute = getattr(UserORM, base_field_name)
                    query = query.where(field >= value)
                continue

            # Ordinary field
            if hasattr(UserORM, field_name):
                field: InstrumentedAttribute = getattr(UserORM, field_name)

                if isinstance(value, str):
                    # For string values looking for an entry
                    query = query.where(field.ilike(f"%{value}%"))
                else:
                    # For other values ​​accurate coincidence
                    query = query.where(field == value)

        return query

    def _apply_sorting(
        self, query: Select, sort_by: Optional[SortBy[UserSortField]]
    ) -> Select:
        if not sort_by:
            return query

        sort_field_name: Optional[Enum] = getattr(sort_by, "field", None)
        sort_direction: Optional[SortDirection] = getattr(sort_by, "direction", None)

        if not sort_field_name or not hasattr(UserORM, sort_field_name.name):
            return query

        field: InstrumentedAttribute = getattr(UserORM, sort_field_name.name)

        if sort_direction and sort_direction == SortDirection.DESC:
            query = query.order_by(field.desc())
        else:
            query = query.order_by(field.asc())

        return query

    def _apply_pagination(
        self, query: Select, pagination: Optional[Pagination]
    ) -> Select:
        if not pagination:
            return query

        return query.offset(pagination.offset).limit(pagination.limit)

    def _setup_to_domain_mapper(self) -> Callable[[UserORM], User]:
        return get_converter(
            src=UserORM,
            dst=User,
            recipe=[
                coercer(uuid.UUID, UserID, lambda uuid: UserID(uuid)),
            ],
        )

    def _setup_to_orm_mapper(self) -> Callable[[User], UserORM]:
        return get_converter(
            src=User,
            dst=UserORM,
            recipe=[
                coercer(UserID, uuid.UUID, lambda user_id: user_id.value),
            ],
        )
