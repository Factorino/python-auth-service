class TokenInvalidError(Exception):
    def __init__(self) -> None:
        super().__init__("Token is invalid")


class TokenExpiredError(Exception):
    def __init__(self) -> None:
        super().__init__("Token has expired")


class TokenRevokedError(Exception):
    def __init__(self) -> None:
        super().__init__("Token has been revoked")
