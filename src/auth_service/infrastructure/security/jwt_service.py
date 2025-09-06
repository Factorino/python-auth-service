from datetime import UTC, datetime, timedelta
from typing import Any, Dict

import jwt as pyjwt
from adaptix import Retort, dumper, loader

from auth_service.core.configurations.jwt import JWTConfig
from auth_service.domain.exceptions.token import (
    TokenExpiredError,
    TokenInvalidError,
)
from auth_service.domain.services.jwt_service import AbstractJWTService
from auth_service.domain.value_objects.jti import JTI
from auth_service.domain.value_objects.jwtpayload import JWTPayload
from auth_service.domain.value_objects.token import TokenType
from auth_service.domain.value_objects.user_id import UserID


class JWTService(AbstractJWTService):
    def __init__(self, config: JWTConfig) -> None:
        self._secret_key: str = config.secret_key
        self._algorithm: str = config.algorithm
        self._access_token_expires_in: int = config.access_token_expires_in
        self._refresh_token_expires_in: int = config.refresh_token_expires_in

        self._mapper: Retort = self._setup_mapper()

    def create_access_token(self, user_id: UserID, jti: JTI) -> str:
        return self._create_token(
            user_id, jti, TokenType.ACCESS, self._access_token_expires_in
        )

    def create_refresh_token(self, user_id: UserID, jti: JTI) -> str:
        return self._create_token(
            user_id, jti, TokenType.REFRESH, self._refresh_token_expires_in
        )

    async def decode_token(self, token: str) -> JWTPayload:
        try:
            payload_dict: Dict[str, Any] = pyjwt.decode(
                jwt=token,
                key=self._secret_key,
                algorithms=[self._algorithm],
                options={"verify_exp": True},
            )
        except pyjwt.ExpiredSignatureError:
            raise TokenExpiredError
        except pyjwt.InvalidTokenError as e:
            raise TokenInvalidError from e

        return self._mapper.load(payload_dict, JWTPayload)

    def _create_token(
        self, user_id: UserID, jti: JTI, token_type: TokenType, expires_in: int
    ) -> str:
        issued_at: datetime = datetime.now(tz=UTC)
        expiration: datetime = issued_at + timedelta(seconds=expires_in)

        payload = JWTPayload(
            sub=user_id,
            jti=jti,
            type=token_type,
            exp=expiration,
            iat=issued_at,
        )

        return pyjwt.encode(
            self._mapper.dump(payload), self._secret_key, algorithm=self._algorithm
        )

    def _setup_mapper(self) -> Retort:
        return Retort(
            recipe=[
                # Convert datetime objects to timestamps (floats) for JWT
                dumper(datetime, lambda dt: dt.timestamp()),
                # Convert timestamps (floats) from JWT back to datetime objects
                loader(float, lambda ts: datetime.fromtimestamp(ts, UTC)),
                # Convert UserID, JTI, TokenType to their string representation for JWT
                dumper(UserID, lambda user_id: str(user_id)),
                dumper(JTI, lambda jti: str(jti)),
                dumper(TokenType, lambda token_type: token_type.value),
                # Convert strings from JWT back to Value Objects
                loader(str, lambda s: UserID.from_string(s)),
                loader(str, lambda s: JTI.from_string(s)),
                loader(str, lambda s: TokenType(s)),
            ]
        )
