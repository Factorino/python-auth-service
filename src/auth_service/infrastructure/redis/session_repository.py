import asyncio
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Set, cast

import orjson
from adaptix import Retort
from redis.asyncio import Redis

from auth_service.domain.entities.session import Session
from auth_service.domain.repositories.session_repository import (
    AbstractSessionRepository,
)
from auth_service.domain.value_objects.jti import JTI
from auth_service.domain.value_objects.user_id import UserID


class RedisSessionRepository(AbstractSessionRepository):
    def __init__(self, redis_client: Redis) -> None:
        self._redis: Redis = redis_client
        self._mapper: Retort = self._setup_mapper()
        self._session_prefix = "session:"
        self._user_sessions_prefix = "user_sessions:"

    async def get_all_by_user_id(self, user_id: UserID) -> List[Session]:
        user_sessions_key: str = self._get_user_sessions_key(user_id)

        jtis: Set[bytes] = await self._redis.smembers(user_sessions_key)  # type: ignore
        if not jtis:
            return []

        sessions: List[Optional[Session]] = await asyncio.gather(
            *[self.get_by_jti(JTI.from_bytes(jti)) for jti in jtis],
            return_exceptions=False,
        )

        return cast(
            List[Session], [session for session in sessions if session is not None]
        )

    async def get_by_jti(self, jti: JTI) -> Optional[Session]:
        session_key: str = self._get_session_key(jti)
        session_data: Optional[bytes] = await self._redis.get(session_key)

        if not session_data:
            return None

        session_dict: Dict[str, Any] = orjson.loads(session_data)
        return self._mapper.load(session_dict, Session)

    async def add(self, session: Session) -> Session:
        session_dict: Dict[str, Any] = self._mapper.dump(session)
        session_data: bytes = orjson.dumps(session_dict)

        session_key: str = self._get_session_key(session.jti)
        user_sessions_key: str = self._get_user_sessions_key(session.user_id)

        ttl: int = self._calculate_ttl(session.expires_at)

        async with self._redis.pipeline() as pipe:
            pipe.setex(session_key, ttl, session_data)
            pipe.sadd(user_sessions_key, str(session.jti))
            pipe.expire(user_sessions_key, ttl)
            await pipe.execute()

        return session

    async def delete(self, jti: JTI) -> Optional[Session]:
        session: Optional[Session] = await self.get_by_jti(jti)
        if not session:
            return None

        session_key: str = self._get_session_key(jti)
        user_sessions_key: str = self._get_user_sessions_key(session.user_id)

        async with self._redis.pipeline() as pipe:
            pipe.delete(session_key)
            pipe.srem(user_sessions_key, str(jti))
            await pipe.execute()

        return session

    async def delete_all_by_user_id(self, user_id: UserID) -> List[Session]:
        user_sessions_key: str = self._get_user_sessions_key(user_id)

        sessions: List[Session] = await self.get_all_by_user_id(user_id)
        if not sessions:
            return []

        session_keys: List[str] = [
            self._get_session_key(session.jti) for session in sessions
        ]

        async with self._redis.pipeline() as pipe:
            pipe.delete(*session_keys)
            pipe.delete(user_sessions_key)
            await pipe.execute()

        return sessions

    def _get_session_key(self, jti: JTI) -> str:
        return f"{self._session_prefix}{jti}"

    def _get_user_sessions_key(self, user_id: UserID) -> str:
        return f"{self._user_sessions_prefix}{user_id}"

    def _calculate_ttl(self, expires_at: datetime) -> int:
        now: datetime = datetime.now(tz=UTC)
        ttl_seconds = int((expires_at - now).total_seconds())
        return max(ttl_seconds, 0)

    def _setup_mapper(self) -> Retort:
        return Retort()
