from auth_service.domain.value_objects import TokenType


class TokenError(Exception):
    pass


class TokenInvalidError(TokenError):
    def __init__(self) -> None:
        super().__init__("Token invalid.")


class TokenExpiredError(TokenError):
    def __init__(self) -> None:
        super().__init__("Token expired.")


class TokenRevokedError(TokenError):
    def __init__(self) -> None:
        super().__init__("Token revoked")


class TokenTypeError(TokenError):
    def __init__(self, expected: TokenType, actual: TokenType) -> None:
        super().__init__(
            f"The type '{expected}' was expected, the '{actual}' was obtained."
        )
