import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from aioredis import Redis

from auth_service.domain.repositories import AbstractSessionRepository
from auth_service.domain.value_objects import JTI, Session, UserId

SESSION_TEMPLETE = "session:{jti}"
USER_SESSIONS_TEMPLATE = "user_sessions:{user_id}"


class RedisSessionRepository(AbstractSessionRepository):
    def __init__(self, redis: Redis) -> None:
        self._redis: Redis = redis

    async def add(self, session: Session) -> None:
        session_key: str = SESSION_TEMPLETE.format(jti=session.jti.value)
        user_sessions_key: str = USER_SESSIONS_TEMPLATE.format(
            user_id=session.user_id.value
        )

        data: Dict[str, Any] = self._session_to_dict(session)
        expires_in: int = self._calculate_ttl(session)

        # Use an atomic update transaction
        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.setex(session_key, expires_in, json.dumps(data))
            pipe.sadd(user_sessions_key, session.jti.value)
            pipe.expire(user_sessions_key, expires_in)
            await pipe.execute()

    async def get_session(self, jti: JTI) -> Optional[Session]:
        session_key: str = SESSION_TEMPLETE.format(jti=jti.value)
        data_json: Optional[str] = await self._redis.get(session_key)

        if not data_json:
            return None

        try:
            data: Dict[str, Any] = json.loads(data_json)
            return self._dict_to_session(data, jti)
        except (KeyError, ValueError):
            return None

    async def get_sessions_by_user_id(self, user_id: UserId) -> List[Session]:
        user_sessions_key: str = USER_SESSIONS_TEMPLATE.format(user_id=user_id.value)

        # Get JTIs for the user
        jtis_bytes: List[bytes] = await self._redis.smembers(user_sessions_key)
        if not jtis_bytes:
            return []

        # Convert bytes to strings and create session keys
        jtis: List[str] = [jti_bytes.decode() for jti_bytes in jtis_bytes]
        session_keys: List[str] = [SESSION_TEMPLETE.format(jti=jti) for jti in jtis]

        # Get all sessions in one request
        sessions_data: List[Optional[str]] = await self._redis.mget(session_keys)

        sessions: List[Session] = []
        for jti_str, data_json in zip(jtis, sessions_data):
            if not data_json:
                continue

            try:
                data: Dict[str, Any] = json.loads(data_json)
                session: Session = self._dict_to_session(data, JTI(jti_str))
                sessions.append(session)
            except (KeyError, ValueError):
                # Delete broken index record
                await self._redis.srem(user_sessions_key, jti_str)
                continue

        return sessions

    async def revoke_session(self, jti: JTI) -> None:
        session_key: str = SESSION_TEMPLETE.format(jti=jti.value)

        # Get current session data to preserve all fields except is_revoked
        data_json: Optional[str] = await self._redis.get(session_key)
        if not data_json:
            return

        try:
            data: Dict[str, Any] = json.loads(data_json)
            data["is_revoked"] = True

            # Update with same TTL
            ttl: int = await self._redis.ttl(session_key)
            if ttl > 0:
                await self._redis.setex(session_key, ttl, json.dumps(data))
        except (KeyError, ValueError):
            # If data is corrupted, just delete the session
            await self._redis.delete(session_key)

    async def revoke_all_sessions(self, user_id: UserId) -> None:
        sessions: List[Session] = await self.get_sessions_by_user_id(user_id)
        for session in sessions:
            await self.revoke_session(session.jti)

    async def is_active(self, jti: JTI) -> bool:
        session: Optional[Session] = await self.get_session(jti)
        return session.is_active() if session else False

    async def cleanup_expired_sessions(self) -> None:
        # Get all index keys
        index_keys_bytes: List[bytes] = await self._redis.keys(
            USER_SESSIONS_TEMPLATE.format("*")
        )
        index_keys: List[str] = [key.decode() for key in index_keys_bytes]

        for index_key in index_keys:
            # Get JTIs from the index
            jtis_bytes: List[bytes] = await self._redis.smembers(index_key)
            jtis: List[str] = [jti.decode() for jti in jtis_bytes]

            if not jtis:
                continue

            # Create session keys and check existence
            session_keys: List[str] = [SESSION_TEMPLETE.format(jti=jti) for jti in jtis]
            exists_results: List[bool] = await self._redis.exists(*session_keys)

            # Remove non-existent sessions from index
            for jti, exists in zip(jtis, exists_results):
                if not exists:
                    await self._redis.srem(index_key, jti)

    def _session_to_dict(self, session: Session) -> Dict[str, Any]:
        return {
            "user_id": session.user_id.value,
            "created_at": session.created_at.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "device_info": session.device_info,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent,
            "is_revoked": session.is_revoked,
        }

    def _dict_to_session(self, data: Dict[str, Any], jti: JTI) -> Session:
        return Session(
            jti=jti,
            user_id=UserId(data["user_id"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            device_info=data["device_info"],
            ip_address=data["ip_address"],
            user_agent=data["user_agent"],
            is_revoked=data["is_revoked"],
        )

    def _calculate_ttl(self, session: Session) -> int:
        return int((session.expires_at - datetime.now(timezone.utc)).total_seconds())
