from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt as pyjwt
from jwt import ExpiredSignatureError, PyJWTError

from auth_service.core.configurations import JWTConfig
from auth_service.domain.exceptions.token import (
    TokenExpiredError,
    TokenInvalidError,
    TokenRevokedError,
)
from auth_service.domain.repositories import AbstractSessionRepository
from auth_service.domain.value_objects import JTI, JWTPayload, TokenType, UserID


class JWTService:
    def __init__(
        self,
        config: JWTConfig,
        session_repository: AbstractSessionRepository,
    ) -> None:
        self._secret_key: str = config.secret_key
        self._algorithm: str = config.algorithm
        self._access_token_expires_in: int = config.access_token_expires_in
        self._refresh_token_expires_in: int = config.refresh_token_expires_in
        self._session_repository: AbstractSessionRepository = session_repository

    def create_access_token(self, user_id: UserID, jti: JTI) -> str:
        return self._create_token(
            user_id, jti, TokenType.ACCESS, self._access_token_expires_in
        )

    def create_refresh_token(self, user_id: UserID, jti: JTI) -> str:
        return self._create_token(
            user_id, jti, TokenType.REFRESH, self._refresh_token_expires_in
        )

    async def decode_token(self, token: str) -> Dict[str, Any]:
        try:
            payload: Any = pyjwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                options={"verify_exp": True},
            )
        except ExpiredSignatureError:
            raise TokenExpiredError
        except PyJWTError as e:
            raise TokenInvalidError from e

        parsed_payload: Dict[str, Any] = self._parse_payload_values(payload)

        # Check is token revoked
        if not await self._session_repository.is_active(parsed_payload["jti"]):
            raise TokenRevokedError

        return parsed_payload

    def _create_token(
        self, user_id: UserID, jti: JTI, token_type: TokenType, expires_in: int
    ) -> str:
        payload = JWTPayload(
            sub=user_id,
            jti=jti,
            type=token_type,
            exp=datetime.now(timezone.utc) + timedelta(seconds=expires_in),
            iat=datetime.now(timezone.utc),
        )
        return pyjwt.encode(
            payload.to_dict(), self._secret_key, algorithm=self._algorithm
        )

    def _parse_payload_values(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            jti = JTI(payload["jti"])
            token_type = TokenType(payload["type"])
            user_id = UserID(payload["sub"])
            exp: datetime = datetime.fromtimestamp(payload["exp"], timezone.utc)
            iat: datetime = datetime.fromtimestamp(payload["iat"], timezone.utc)
        except (ValueError, TypeError) as e:
            raise TokenInvalidError from e

        return {
            "sub": user_id,
            "jti": jti,
            "type": token_type,
            "exp": exp,
            "iat": iat,
        }
